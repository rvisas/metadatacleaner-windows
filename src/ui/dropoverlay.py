# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, GObject, Gtk


class DropOverlay(Adw.Bin):
    __gtype_name__ = "DropOverlay"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.overlay = Gtk.Overlay()
        self.status_page = Adw.StatusPage(
            icon_name="metadatacleaner-paper-symbolic",
            css_classes=["status"],
        )

        self.revealer = Gtk.Revealer(
            child=self.status_page,
            can_target=False,
            transition_type=Gtk.RevealerTransitionType.CROSSFADE,
            transition_duration=800,
        )

        self.overlay.add_overlay(self.revealer)
        self.set_child(self.overlay)
        self.add_css_class("dropoverlay")

    @GObject.Property(type=Gtk.Widget)
    def overlay_child(self) -> Gtk.Widget:
        return self.overlay.get_child()

    @overlay_child.setter  # type: ignore
    def overlay_child(self, value: Gtk.Widget):
        self.overlay.set_child(value)

    @GObject.Property(type=bool, default=False)
    def dropping(self) -> bool:
        return self.revealer.get_reveal_child()

    @dropping.setter  # type: ignore
    def dropping(self, value: bool):
        self.revealer.set_reveal_child(value)

    @GObject.Property(type=str)
    def title(self) -> str:
        return self.status_page.get_title()

    @title.setter  # type: ignore
    def title(self, value: str):
        self.status_page.set_title(value)

    @GObject.Property(type=bool, default=False)
    def compact(self) -> bool:
        return self.status_page.has_css_class("compact")

    @compact.setter  # type: ignore
    def compact(self, value: bool):
        if self.compact != value:
            if value:
                self.status_page.add_css_class("compact")
            else:
                self.status_page.remove_css_class("compact")

    @GObject.Property(type=str)
    def icon_name(self) -> str:
        return self.status_page.get_icon_name()

    @icon_name.setter  # type: ignore
    def icon_name(self, value: str):
        self.status_page.set_icon_name(value)
