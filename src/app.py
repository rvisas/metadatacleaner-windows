# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Application for Metadata Cleaner."""

import os
import subprocess
import time
from gettext import gettext as _
from threading import Thread

from gi.repository import Adw, Gdk, Gio, GLib, GObject
from metadatacleaner.modules import updater
from metadatacleaner.modules.logger import Logger as logger
from metadatacleaner.ui.window import Window


class MetadataCleaner(Adw.Application):
    """Application for Metadata Cleaner."""

    __gtype_name__ = "MetadataCleaner"

    devel = GObject.Property(type=bool, default=False)
    settings = GObject.Property(type=Gio.Settings)
    version = GObject.Property(type=str)

    def __init__(self, devel: bool, version: str, *args, **kwargs) -> None:
        """Application initialization.

        Args:
            app_id (str): Application ID
            version (str): Version string
        """
        super().__init__(
            flags=Gio.ApplicationFlags.HANDLES_OPEN, *args, **kwargs
        )
        # translators: app name
        self.name = _("Metadata Cleaner")
        self.devel = devel
        self.version = version
        self.settings = Gio.Settings.new(self.get_application_id())
        self._update_check_running = False
        self._update_downloading = False

    # APPLICATION METHODS #

    def do_activate(self) -> None:
        """Run on application activation."""
        self.new_window()

    def do_startup(self) -> None:
        """Run on application startup."""
        Adw.Application.do_startup(self)
        self._setup_actions()
        self._setup_accels()
        GLib.idle_add(self._schedule_update_check)

    def do_open(self, gfiles: list[Gio.File], n_files: int, hint: str) -> None:
        """Run when files are passed to the command line."""
        self.new_window(gfiles=gfiles)

    # SETUP #

    def _setup_actions(self) -> None:
        def on_show_window(
            action: Gio.Action, parameters: GLib.Variant
        ) -> None:
            window_id = parameters.get_uint32()
            window = self.get_window_by_id(window_id)
            window.present_with_time(Gdk.CURRENT_TIME)
            self.withdraw_notification(f"done{window_id}")

        show_window = Gio.SimpleAction.new(
            "show-window", GLib.VariantType.new("u")
        )
        show_window.connect("activate", on_show_window)
        self.add_action(show_window)

        def on_new_window(action: Gio.Action, parameters: None) -> None:
            self.new_window()

        new_window = Gio.SimpleAction.new("new-window", None)
        new_window.connect("activate", on_new_window)
        self.add_action(new_window)

        def on_quit_app(action: Gio.Action, parameters: None) -> None:
            for window in self.get_windows():
                self.withdraw_notification(f"done{window.get_id()}")
            self.quit()

        quit_app = Gio.SimpleAction.new("quit", None)
        quit_app.connect("activate", on_quit_app)
        self.add_action(quit_app)

        self.add_action(self.settings.create_action("lightweight-cleaning"))
        self.add_action(self.settings.create_action("check-for-updates"))

        def on_check_updates(action: Gio.Action, parameters: None) -> None:
            self.check_for_updates(manual=True)

        check_updates = Gio.SimpleAction.new("check-updates", None)
        check_updates.connect("activate", on_check_updates)
        self.add_action(check_updates)

    def _setup_accels(self) -> None:
        self.set_accels_for_action("app.new-window", ["<Control>n"])
        self.set_accels_for_action("app.quit", ["<Control>q"])
        self.set_accels_for_action("win.add-files", ["<Control>o"])
        self.set_accels_for_action("win.add-folders", ["<Control><Shift>o"])
        self.set_accels_for_action("win.clear-files", ["<Control>r"])
        self.set_accels_for_action("win.clean-metadata", ["<Control>m"])
        self.set_accels_for_action("win.close", ["<Control>w"])

    # PUBLIC #

    def check_for_updates(self, manual: bool = True) -> None:
        """Check GitHub for a newer Windows build.

        Automatic checks are rate-limited to one per day; a manual check
        ignores that interval.
        """
        self._maybe_check_for_updates(force=manual)

    def _schedule_update_check(self) -> bool:
        """Run the automatic check after the first window is ready."""
        self._maybe_check_for_updates()
        return GLib.SOURCE_REMOVE

    def _maybe_check_for_updates(self, force: bool = False) -> None:
        if self._update_check_running:
            return
        if not force:
            if self.devel:
                return
            if not self.settings.get_boolean("check-for-updates"):
                return
            now = int(time.time())
            last = self.settings.get_int64("last-update-check")
            if last and now - last < 24 * 60 * 60:
                return
        self._update_check_running = True
        Thread(
            target=self._check_for_updates_async,
            args=(force,),
            daemon=True,
        ).start()

    def _check_for_updates_async(self, manual: bool) -> None:
        update = None
        error = None
        try:
            update = updater.pick_update(
                updater.fetch_releases(), self.version
            )
        except Exception as exc:
            error = exc
        GLib.idle_add(self._on_update_checked, update, manual, error)

    def _on_update_checked(
        self,
        update: updater.Update | None,
        manual: bool,
        error: Exception | None,
    ) -> bool:
        self._update_check_running = False
        window = self._active_window()
        if error is not None:
            logger.warning(f"Could not check for updates: {error}")
            if manual and window is not None:
                window.show_toast(_("Could not check for updates."))
            return GLib.SOURCE_REMOVE
        self.settings.set_int64("last-update-check", int(time.time()))
        if update is None:
            if manual and window is not None:
                window.show_toast(_("You are using the latest version."))
            return GLib.SOURCE_REMOVE
        if window is not None:
            self._present_update(update, window)
        return GLib.SOURCE_REMOVE

    def _active_window(self) -> Window | None:
        window = self.get_active_window()
        if window is not None:
            return window
        windows = self.get_windows()
        return windows[0] if windows else None

    def _present_update(self, update: updater.Update, window: Window) -> None:
        dialog = Adw.AlertDialog.new(
            _("A new version is available"),
            _(
                "Metadata Cleaner {version} is ready. Click “Update now” "
                "to download and install it."
            ).format(version=update.version),
        )
        dialog.add_response("later", _("Later"))
        dialog.add_response("install", _("Update now"))
        dialog.set_response_appearance(
            "install", Adw.ResponseAppearance.SUGGESTED
        )
        dialog.set_close_response("later")
        dialog.connect("response", self._on_update_dialog_response, update)
        dialog.present(window)

    def _on_update_dialog_response(
        self,
        dialog: Adw.AlertDialog,
        response: str,
        update: updater.Update,
    ) -> None:
        if response != "install":
            return
        window = self._active_window()
        if window is None:
            return
        if self._update_downloading:
            return
        self._update_downloading = True
        window.show_toast(_("Downloading update…"))
        Thread(
            target=self._download_update_async,
            args=(update,),
            daemon=True,
        ).start()

    def _download_update_async(self, update: updater.Update) -> None:
        path = None
        error = None
        try:
            path = updater.download_update(update)
        except Exception as exc:
            error = exc
        GLib.idle_add(self._on_update_downloaded, path, error)

    def _on_update_downloaded(
        self, path: object, error: Exception | None
    ) -> bool:
        self._update_downloading = False
        window = self._active_window()
        if error is not None:
            logger.warning(f"Could not download the update: {error}")
            if window is not None:
                window.show_toast(_("Could not download the update."))
            return GLib.SOURCE_REMOVE
        if os.name != "nt" or path is None:
            if window is not None:
                window.show_toast(_("The update was downloaded."))
            return GLib.SOURCE_REMOVE
        try:
            subprocess.Popen([str(path)])
        except OSError as exc:
            logger.warning(f"Could not start the update installer: {exc}")
            if window is not None:
                window.show_toast(_("Could not start the update installer."))
            return GLib.SOURCE_REMOVE
        self.quit()
        return GLib.SOURCE_REMOVE

    def new_window(self, gfiles: list[Gio.File] | None = None) -> None:
        """Create a new window.

        Args:
            gfiles (List[Gio.File], optional): List of files to be added to the
                new window. Defaults to None.
        """

        def on_window_destroyed(window) -> None:
            self.withdraw_notification(f"done{window.get_id()}")

        window = Window(application=self)
        window.connect("destroy", on_window_destroyed)
        window.present()
        if gfiles:
            window.file_store.add_gfiles(gfiles)
