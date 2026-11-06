# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""File object and states."""

import hashlib
import os
import re
import tempfile
from enum import IntEnum, auto
from gettext import gettext as _
from pathlib import Path

from gi.repository import Gio, GLib, GObject
from libmat2 import parser_factory
from metadatacleaner.modules.logger import Logger as logger
from metadatacleaner.modules.metadata import (
    Metadata,
    MetadataFile,
    MetadataList,
    MetadataStore,
)


class FileState(IntEnum):
    """States that a File can have."""

    INITIALIZING = auto()
    ERROR_WHILE_INITIALIZING = auto()
    UNSUPPORTED = auto()
    SUPPORTED = auto()
    CHECKING_METADATA = auto()
    ERROR_WHILE_CHECKING_METADATA = auto()
    HAS_NO_METADATA = auto()
    HAS_METADATA = auto()
    REMOVING_METADATA = auto()
    ERROR_WHILE_REMOVING_METADATA = auto()
    CLEANED = auto()


class File(GObject.GObject):
    """File object."""

    __gtype_name__ = "File"

    __gsignals__ = {"state-changed": (GObject.SIGNAL_RUN_LAST, None, (int,))}

    filename = GObject.Property(type=str)
    directory = GObject.Property(type=str)
    display_directory = GObject.Property(
        type=bool, nick="display-directory", default=True
    )
    icon_name = GObject.Property(type=str, nick="icon-name")
    simple_state = GObject.Property(
        type=str, nick="simple-state", default="working"
    )
    metadata = GObject.Property(type=MetadataStore)
    total_metadata = GObject.Property(
        type=int, nick="total-metadata", default=0
    )
    selectable = GObject.Property(type=bool, default=False)
    message_type = GObject.Property(
        type=str, nick="message-type", default="none"
    )
    has_message = GObject.Property(
        type=bool, nick="has-message", default=False
    )

    def __init__(self, gfile: Gio.File) -> None:
        """File initialization.

        Args:
            gfile (Gio.File): The Gio File that the File will be built from.
        """
        super().__init__()
        self._gfile = gfile
        self._temp_path = self._compute_temp_path(gfile.get_path())
        self.path = gfile.get_path()
        self.filename = gfile.get_basename()
        self._extract_path(gfile)
        self.state = FileState.INITIALIZING
        self.mimetype = "text/plain"
        self.icon_name = Gio.content_type_get_generic_icon_name(self.mimetype)
        self.metadata = MetadataStore()
        self.error: Exception | None = None

    def _compute_temp_path(self, path: str) -> str:
        # We have to keep the extension so that ffmpeg doesn't break
        digest = hashlib.sha256(path.encode("utf-8")).hexdigest()
        return str(
            Path(tempfile.gettempdir()) / f"{digest}{Path(path).suffix}"
        )

    def _simplify_dir_path(self, path: str) -> None:
        dir_path = str(Path(path).parent)
        doc_path_match = re.match(r"/run/user/\d+/doc/[a-z\d]+/?", dir_path)
        if doc_path_match:
            # Remove the Document Store path
            dir_path = dir_path.replace(doc_path_match.group(0), "", 1)
        elif dir_path.startswith(GLib.get_home_dir()):
            # Replace the home path with the friendly ~
            dir_path = dir_path.replace(GLib.get_home_dir(), "~", 1)
        self.directory = dir_path
        self.display_directory = bool(dir_path)

    def _extract_path(self, gfile: Gio.File) -> None:
        self._simplify_dir_path(gfile.get_path())
        # The document portal xattr only exists inside a Flatpak sandbox.
        # Querying it on Windows raises once per file and spams the log.
        if os.name == "nt":
            return
        if gfile:
            gfile.query_info_async(
                "xattr::document-portal.host-path",
                Gio.FileQueryInfoFlags.NONE,
                GLib.PRIORITY_DEFAULT,
                None,
                self.on_gfile_info_cb,
            )

    def on_gfile_info_cb(
        self, gfile: Gio.File, result: Gio.AsyncResult
    ) -> None:
        try:
            info = gfile.query_info_finish(result)
            path = info.get_attribute_string(
                "xattr::document-portal.host-path"
            )
            if path:
                self._simplify_dir_path(path)
        except GLib.Error:
            logger.error("Could not query file: {e.code} {e.message}")

    def _set_state(self, state: FileState) -> None:
        if state == self.state or self.state == FileState.CLEANED:
            return

        def update_state(state) -> bool:
            simple_states = {
                FileState.INITIALIZING: "working",
                FileState.ERROR_WHILE_INITIALIZING: "error",
                FileState.UNSUPPORTED: "error",
                FileState.SUPPORTED: "working",
                FileState.CHECKING_METADATA: "working",
                FileState.ERROR_WHILE_CHECKING_METADATA: "error",
                FileState.HAS_NO_METADATA: "warning",
                FileState.HAS_METADATA: "has-metadata",
                FileState.REMOVING_METADATA: "working",
                FileState.ERROR_WHILE_REMOVING_METADATA: "error",
                FileState.CLEANED: "clean",
            }
            message_types = {
                FileState.INITIALIZING: "none",
                FileState.ERROR_WHILE_INITIALIZING: "error-initializing",
                FileState.UNSUPPORTED: "unsupported",
                FileState.SUPPORTED: "none",
                FileState.CHECKING_METADATA: "none",
                FileState.ERROR_WHILE_CHECKING_METADATA: "error-checking",
                FileState.HAS_NO_METADATA: "no-metadata",
                FileState.HAS_METADATA: "none",
                FileState.REMOVING_METADATA: "none",
                FileState.ERROR_WHILE_REMOVING_METADATA: "error-removing",
                FileState.CLEANED: "none",
            }
            self.simple_state = simple_states[state]
            self.selectable = state == FileState.HAS_METADATA
            self.message_type = message_types[state]
            self.has_message = self.message_type != "none"
            self.emit("state-changed", state)
            return GLib.SOURCE_REMOVE

        GLib.idle_add(update_state, state)
        self.state = state

    def check_metadata(self) -> None:
        """Set up the parser and check the metadata present in the file."""
        try:
            parser, mimetype = parser_factory.get_parser(self.path)
        except Exception as e:
            self._setup_parser_error(e)
        else:
            self._setup_parser_finish(parser, mimetype)

        if self.state != FileState.SUPPORTED:
            return
        self._set_state(FileState.CHECKING_METADATA)
        try:
            metadata = self._parser.get_meta()
        except Exception as e:
            self._check_metadata_error(e)
        else:
            self._check_metadata_finish(metadata)

    def _setup_parser_error(self, error: Exception) -> None:
        self.error = error
        logger.warning(
            f"Error while setting up parser for {self.filename}: {error}"
        )
        self._set_state(FileState.ERROR_WHILE_INITIALIZING)

    def _setup_parser_finish(self, parser, mimetype) -> None:
        self._parser = parser
        if mimetype:

            def update_mimetype(mimetype) -> bool:
                self.mimetype = mimetype
                self.icon_name = Gio.content_type_get_generic_icon_name(
                    self.mimetype
                )
                return GLib.SOURCE_REMOVE

            GLib.idle_add(update_mimetype, mimetype)
        if self._parser:
            self._set_state(FileState.SUPPORTED)
        else:
            self._set_state(FileState.UNSUPPORTED)

    def _check_metadata_error(self, error: Exception) -> None:
        self.error = error
        logger.warning(
            f"Error while checking metadata for {self.filename}: {error}"
        )
        self._set_state(FileState.ERROR_WHILE_CHECKING_METADATA)

    def _check_metadata_finish(self, metadata) -> None:
        if not bool(metadata):
            self._set_state(FileState.HAS_NO_METADATA)
            return
        total_metadata = 0
        # Metadata found in multiple files (e.g. in archive)
        if isinstance(metadata[list(metadata)[0]], dict):
            for filename, file_metadata in metadata.items():
                metadata_list = MetadataList()
                for key, value in file_metadata.items():
                    metadata_list.append(Metadata(key=key, value=value))
                self.metadata.append(
                    MetadataFile(
                        filename=Path(self.filename) / filename,
                        metadata=metadata_list,
                    )
                )
                total_metadata += len(metadata_list)
        # Metadata found in a single file
        else:
            metadata_list = MetadataList()
            for key, value in metadata.items():
                metadata_list.append(Metadata(key=key, value=value))
            self.metadata.append(
                MetadataFile(filename=self.filename, metadata=metadata_list)
            )
            total_metadata += len(metadata_list)

        def update_total_metadata(total_metadata) -> bool:
            self.total_metadata = total_metadata
            return GLib.SOURCE_REMOVE

        GLib.idle_add(update_total_metadata, total_metadata)
        self._set_state(FileState.HAS_METADATA)

    def clean(self, lightweight_mode=False) -> None:
        """Clean the metadata from the file.

        Args:
            lightweight_mode (bool, optional): Use mat2 lightweight mode to
                preserve data integrity. Defaults to False.
        """
        if self.state not in [
            FileState.HAS_METADATA,
            FileState.HAS_NO_METADATA,
        ]:
            return
        self._set_state(FileState.REMOVING_METADATA)
        try:
            self._parser.output_filename = self._temp_path
            self._parser.lightweight_cleaning = lightweight_mode
            result = self._parser.remove_all()
            if result is False:
                # translators: generic error message shown when the cleaning
                #              was unsuccessful but we don't know why
                raise RuntimeError(_("An error occurred during the cleaning."))
            if not Path(self._temp_path).exists():
                raise RuntimeError(
                    _(
                        # translators: error message when a file is no longer
                        #              available during cleaning. "Something
                        #              bad happened" as in "Something went
                        #              wrong"
                        "Something bad happened during the cleaning, "
                        "cleaned file not found"
                    )
                )
            cleaned_gfile = Gio.File.new_for_path(self._temp_path)
            cleaned_gfile.move(
                self._gfile, Gio.FileCopyFlags.OVERWRITE, None, None, None
            )
        except Exception as e:
            self._clean_error(e)
        else:
            self._clean_finish()

    def _clean_error(self, error: Exception) -> None:
        self.error = error
        logger.warning(
            f"Error while cleaning metadata from {self.filename}: {error}"
        )
        self._set_state(FileState.ERROR_WHILE_REMOVING_METADATA)

    def _clean_finish(self) -> None:
        self._set_state(FileState.CLEANED)
