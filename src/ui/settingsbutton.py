# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Settings button."""

from gi.repository import Adw, Gtk
from metadatacleaner import RESOURCE_PATH


@Gtk.Template(resource_path=RESOURCE_PATH + "/ui/SettingsButton.ui")
class SettingsButton(Gtk.Button):
    """Settings button."""

    __gtype_name__ = "SettingsButton"

    _preferences_dlg: Adw.PreferencesDialog = Gtk.Template.Child()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.connect("clicked", self.show_pref_dialog)

    def show_pref_dialog(self, button: Gtk.Button) -> None:
        self._preferences_dlg.present(self.get_root())
