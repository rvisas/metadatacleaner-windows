# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Files Manager object and states."""

import mimetypes
import os
from collections.abc import Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import IntEnum, auto
from threading import Lock, Thread

import libmat2
from gi.repository import Gio, GLib, GObject
from metadatacleaner.modules.file import File, FileState
from metadatacleaner.modules.logger import Logger as logger


def _get_supported_formats() -> dict:
    formats = {}
    for parser in libmat2.parser_factory._get_parsers():
        for mimetype in parser.mimetypes:
            extensions = set()
            for extension in mimetypes.guess_all_extensions(mimetype):
                if extension not in libmat2.UNSUPPORTED_EXTENSIONS:
                    extensions.add(extension)
            if not extensions:
                continue
            formats[mimetype] = extensions
    return formats


SUPPORTED_FORMATS = _get_supported_formats()


class FileStoreState(IntEnum):
    """States the Files Manager can have."""

    IDLE = auto()
    WORKING = auto()


class FileStoreAction(IntEnum):
    """Actions the Files manager can do."""

    ADDING = auto()
    CLEANING = auto()


class FileStore(Gio.ListStore):
    """File Store object."""

    __gtype_name__ = "FileStore"

    # A GFileInfo created by an enumerator only contains the attributes that
    # were requested.  Asking for an empty attribute list makes every child
    # look like G_FILE_TYPE_UNKNOWN, so folder imports silently add nothing.
    _DIRECTORY_ATTRIBUTES = "standard::name,standard::type"

    __gsignals__ = {
        "file-state-changed": (GObject.SIGNAL_RUN_LAST, None, (int,)),
        "state-changed": (GObject.SIGNAL_RUN_LAST, None, (int,)),
        "progress-changed": (GObject.SIGNAL_RUN_LAST, None, (int, int)),
    }

    lightweight_mode: bool = GObject.Property(
        type=bool, nick="lightweight-mode", default=False
    )

    def __init__(self) -> None:
        """File Store initialization."""
        Gio.ListStore.__init__(self, item_type=File)
        self.state = FileStoreState.IDLE
        self.last_action: FileStoreAction | None = None
        self.progress = (0, 0)
        # Reuse a single pool for the whole application.  Creating one pool per
        # directory (as the original recursive walker did) creates a thread per
        # directory and makes large folder imports slower, not faster.
        self.add_files_executor = ThreadPoolExecutor(
            max_workers=min(8, (os.cpu_count() or 4)),
            thread_name_prefix="metadata-cleaner-add",
        )
        self.clean_files_executor = ThreadPoolExecutor()
        # Duplicate detection used to scan the whole ListStore for every file,
        # which is O(n^2).  Keep an O(1) index next to the model instead.
        self._known_paths: set[str] = set()
        self._known_paths_lock = Lock()
        # Progress updates can arrive once per discovered/completed file.  A
        # single pending idle callback is enough; emitting thousands of them
        # slows down imports without making the bar more accurate.
        self._progress_update_scheduled = False

    def _on_file_state_changed(self, f: File, new_state: FileState) -> None:
        def emit() -> bool:
            self.emit("file-state-changed", self.get_index_of_file(f))
            return GLib.SOURCE_REMOVE

        GLib.idle_add(emit)

    def _set_state(self, state: FileStoreState) -> None:
        if state == self.state:
            return
        self.state = state

        def emit() -> bool:
            self.emit("state-changed", state)
            return GLib.SOURCE_REMOVE

        GLib.idle_add(emit)

    def _set_progress(self, current: int, total: int) -> None:
        self.progress = (current, total)
        if self._progress_update_scheduled:
            return
        self._progress_update_scheduled = True

        def emit() -> bool:
            self._progress_update_scheduled = False
            self.emit("progress-changed", *self.progress)
            return GLib.SOURCE_REMOVE

        GLib.idle_add(emit)

    def get_files(self) -> list[File]:
        """Get all the files from the File Store.

        Returns:
            List[File]: List of files.
        """
        return self

    def get_file_with_index(self, index: int) -> File:
        """Get a file at a specified index.

        Args:
            index (int): The desired index.

        Returns:
            Optional[File]: The file if found, else None.
        """
        f = self.get_item(index)
        if not f:
            raise RuntimeError("No file in the file store for this index.")
        return f

    def get_index_of_file(self, f: File) -> int:
        """Get the index of a given file.

        Args:
            f (File): The file to get the index for.

        Returns:
            int: The file index.
        """
        found, position = self.find(f)
        if not found:
            raise RuntimeError("File not found in file store.")
        return position

    def add_gfiles(
        self, gfiles: list[Gio.File], recursive: bool = True
    ) -> None:
        """Add Gio Files to the Files Manager.

        Args:
            gfiles (List[Gio.File]): List of Gio Files to add.
            recursive (bool, optional): If subdirectories should also be looked
            into. Defaults to True.
        """
        thread = Thread(
            target=self._add_gfiles_async,
            args=(gfiles, recursive),
            daemon=True,
        )
        thread.start()

    def _add_gfiles_async(
        self, gfiles: list[Gio.File], recursive: bool = True
    ) -> None:
        """Discover and add files without waiting for the whole tree first.

        The previous implementation built the complete file list before adding
        the first row.  On a large folder that left the window empty for the
        entire directory scan.  This version streams discovery into the add
        pool, so rows appear as soon as the first files are found.  The row is
        appended before ``check_metadata`` runs, which keeps the interface
        responsive while mat2 reads each file.
        """
        try:
            self._set_state(FileStoreState.WORKING)
            self.last_action = FileStoreAction.ADDING
            self._set_progress(0, 0)

            futures = []
            discovered = 0
            for gfile in self._iter_gfiles(gfiles, recursive):
                discovered += 1
                self._set_progress(self.progress[0], discovered)
                futures.append(
                    self.add_files_executor.submit(self._add_gfile, gfile)
                )

            if not futures:
                return

            for _ in as_completed(futures):
                self._set_progress(self.progress[0] + 1, discovered)
        except Exception as error:
            logger.error(f"Error while adding files: {error}")
        finally:
            self._stop_adding_gfiles()

    def _iter_gfiles(
        self, gfiles: list[Gio.File], recursive: bool = True
    ) -> Iterator[Gio.File]:
        """Yield regular files from a mixed list of files and directories."""
        for gfile in gfiles:
            if not gfile:
                continue
            try:
                f_type = gfile.query_file_type(
                    Gio.FileQueryInfoFlags.NONE, None
                )
            except GLib.Error as error:
                logger.warning(
                    f"Could not inspect {gfile.get_path()}: {error.message}"
                )
                continue
            if f_type == Gio.FileType.DIRECTORY:
                yield from self._iter_gfiles_from_dir(gfile, recursive)
            elif f_type == Gio.FileType.REGULAR:
                yield gfile
            else:
                logger.warning(
                    f"File {gfile.get_path()} is neither a directory nor a "
                    "regular file, skipping."
                )

    def _gather_all_gfiles(
        self, gfiles: list[Gio.File], recursive: bool = True
    ) -> list[Gio.File]:
        return list(self._iter_gfiles(gfiles, recursive))

    def _iter_gfiles_from_dir(
        self, dir: Gio.File, recursive: bool
    ) -> Iterator[Gio.File]:
        """Walk a directory iteratively.

        An iterative stack avoids both Python recursion limits and the nested
        ``ThreadPoolExecutor`` that used to be created for every subdirectory.
        """
        pending = [dir]
        while pending:
            current = pending.pop()
            enumerator = None
            try:
                enumerator = current.enumerate_children(
                    self._DIRECTORY_ATTRIBUTES,
                    Gio.FileQueryInfoFlags.NONE,
                    None,
                )
                while True:
                    info = enumerator.next_file(None)
                    if info is None:
                        break
                    child = enumerator.get_child(info)
                    f_type = info.get_file_type()
                    if f_type == Gio.FileType.DIRECTORY:
                        if recursive:
                            pending.append(child)
                    elif f_type == Gio.FileType.REGULAR:
                        yield child
            except GLib.Error as error:
                logger.warning(
                    f"Could not read {current.get_path()}: {error.message}"
                )
            finally:
                if enumerator is not None:
                    enumerator.close(None)

    def _get_gfiles_from_dir(
        self, dir: Gio.File, recursive: bool
    ) -> list[Gio.File]:
        """Return the files in a directory tree.

        Kept as a list-returning compatibility wrapper for callers and tests;
        the implementation now uses one iterative walker.
        """
        return list(self._iter_gfiles_from_dir(dir, recursive))

    def _add_gfile(self, gfile: Gio.File) -> None:
        if gfile is None:
            logger.warning("File is None, skipping.")
            return

        path = gfile.get_path()
        if not path:
            logger.warning("File has no local path, skipping.")
            return

        # Reserve the path before the expensive parser work.  This removes the
        # O(n^2) ListStore scan and also prevents two workers from adding the
        # same file concurrently.
        with self._known_paths_lock:
            if path in self._known_paths:
                logger.warning(f"Skipping {path}, already added.")
                return
            self._known_paths.add(path)

        try:
            if not gfile.query_exists(None):
                logger.warning(f"File {path} does not exist, skipping.")
                with self._known_paths_lock:
                    self._known_paths.discard(path)
                return

            f = File(gfile)
            f.connect("state-changed", self._on_file_state_changed)

            def append_file() -> bool:
                self.append(f)
                return GLib.SOURCE_REMOVE

            # Put the row in the list immediately.  mat2 parsing happens after
            # this idle callback and updates the row when it finishes.
            GLib.idle_add(append_file)
            f.check_metadata()
        except Exception as error:
            logger.warning(f"Could not add {path}: {error}")
            with self._known_paths_lock:
                self._known_paths.discard(path)

    def _stop_adding_gfiles(self) -> None:
        self.add_files_executor.shutdown(wait=False, cancel_futures=True)
        self.add_files_executor = ThreadPoolExecutor(
            max_workers=min(8, (os.cpu_count() or 4)),
            thread_name_prefix="metadata-cleaner-add",
        )
        self._set_state(FileStoreState.IDLE)
        self._set_progress(0, 0)

    def cancel_addding_gfiles(self) -> None:
        """Cancel adding GFiles."""
        self._stop_adding_gfiles()

    def remove_file(self, f: File) -> None:
        """Remove a file from the File Store.

        Args:
            f (File): The file to remove.
        """
        self.remove_file_with_index(self.get_index_of_file(f))

    def remove_file_with_index(self, index: int) -> None:
        """Remove the file with the given index from the File Store.

        Args:
            index (int): The index of the file to remove.
        """
        f = self.get_file_with_index(index)
        self.remove(index)
        with self._known_paths_lock:
            self._known_paths.discard(f.path)

    def remove_files(self) -> None:
        """Remove all the files from the File Store."""
        self.remove_all()
        with self._known_paths_lock:
            self._known_paths.clear()

    def clean_files(self) -> None:
        """Remove metadata from all the cleanable files."""
        thread = Thread(target=self._clean_files_async, daemon=True)
        thread.start()

    def _clean_files_async(self) -> None:
        cleanable_files = self.get_cleanable_files()
        self._set_progress(
            self.progress[0], self.progress[1] + len(cleanable_files)
        )
        self._set_state(FileStoreState.WORKING)
        self.last_action = FileStoreAction.CLEANING
        futures = {
            self.clean_files_executor.submit(f.clean, self.lightweight_mode)
            for f in cleanable_files
        }
        for future in as_completed(futures):
            current = self.progress[0] + 1
            total = self.progress[1]
            self._set_progress(current, total)
        self._stop_cleaning_files()

    def _stop_cleaning_files(self) -> None:
        self.clean_files_executor.shutdown(wait=False, cancel_futures=True)
        self.clean_files_executor = ThreadPoolExecutor()
        self._set_state(FileStoreState.IDLE)
        self._set_progress(0, 0)

    def cancel_cleaning_files(self) -> None:
        """Cancel the cleaning process."""
        self._stop_cleaning_files()

    def get_cleanable_files(self) -> list[File]:
        """Get all the cleanable files.

        Returns:
            List[File]: List of cleanable files.
        """
        return self._get_files_with_states(
            (FileState.HAS_METADATA, FileState.HAS_NO_METADATA)
        )

    def get_cleaned_files(self) -> list[File]:
        """Get all the cleaned files.

        Returns:
            List[File]: List of cleaned files.
        """
        return self._get_files_with_states((FileState.CLEANED,))

    def get_errored_files(self) -> list[File]:
        """Get all the files with errors.

        Returns:
            List[File]: List of files with errors.
        """
        return self._get_files_with_states(
            (
                FileState.ERROR_WHILE_INITIALIZING,
                FileState.ERROR_WHILE_CHECKING_METADATA,
                FileState.ERROR_WHILE_REMOVING_METADATA,
            )
        )

    def _get_files_with_states(
        self, states: Iterable[FileState]
    ) -> list[File]:
        return list(filter(lambda f: f.state in states, self))
