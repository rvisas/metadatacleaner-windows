# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Badge to display information."""

from gettext import gettext as _

from gi.repository import Adw, GObject, Gtk
from metadatacleaner import RESOURCE_PATH


@Gtk.Template(resource_path=RESOURCE_PATH + "/ui/Badge.ui")
class Badge(Adw.Bin):
    """Badge to display information."""

    __gtype_name__ = "Badge"
    _state = ""
    _label = ""

    @GObject.Property(type=str, default="")
    def label(self):
        """Get the badge label.

        Returns:
            str: The badge label.
        """
        return self._label

    @label.setter  # type: ignore
    def label(self, value):
        self._label = value

    @GObject.Property(type=str, default="")
    def state(self):
        """Get the current badge state.

        working => spinner
        warning => !
        error => -
        clean => checkmark
        has-metadata => label

        Returns:
            str: The badge state.
        """
        return self._state

    @state.setter  # type: ignore
    def state(self, value):
        if self._state == value:
            return
        self._state = value
        self._reset()
        match value:
            case "working":
                self.set_child(Gtk.Spinner(spinning=True))
            case "warning":
                self.add_css_class("warning")
                self.set_child(
                    Gtk.Image(
                        icon_name="metadatacleaner-warning-symbolic",
                        # translators: tooltip text on the badge that shows an
                        #              icon representing the state of the file
                        tooltip_text=_("Warning"),
                    )
                )
            case "error":
                self.add_css_class("error")
                self.set_child(
                    Gtk.Image(
                        icon_name="metadatacleaner-error-symbolic",
                        # translators: tooltip text on the badge that shows an
                        #              icon representing the state of the file
                        tooltip_text=_("Error"),
                    )
                )
            case "has-metadata":
                self.add_css_class("metadata")
                label = Gtk.Label(css_classes=["numeric"], label=self._label)
                self.bind_property("label", label, "label")
                self.set_child(label)
            case "clean":
                self.add_css_class("success")
                self.set_child(
                    Gtk.Image(
                        icon_name="metadatacleaner-ok-symbolic",
                        # translators: tooltip text on the badge that shows an
                        #              icon representing the state of the file
                        tooltip_text=_("Cleaned"),
                    )
                )

    def _reset(self):
        self.set_css_classes(["badge"])
        self.set_child(None)
