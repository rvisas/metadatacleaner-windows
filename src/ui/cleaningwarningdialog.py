# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Dialog warning the user of possible data loss on cleaning."""

from gi.repository import Adw, Gio, GObject, Gtk
from metadatacleaner import RESOURCE_PATH


@Gtk.Template(resource_path=RESOURCE_PATH + "/ui/CleaningWarningDialog.ui")
class CleaningWarningDialog(Adw.AlertDialog):
    """Dialog warning the user of possible data loss on cleaning."""

    __gtype_name__ = "CleaningWarningDialog"

    settings = GObject.Property(type=Gio.Settings)

    _checkbutton: Gtk.CheckButton = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def _on_settings_changed(
        self, checkbox, p_spec: GObject.ParamSpec
    ) -> None:
        if not self.settings:
            return
        self.settings.set_boolean(
            "cleaning-without-warning", self._checkbutton.get_active()
        )
