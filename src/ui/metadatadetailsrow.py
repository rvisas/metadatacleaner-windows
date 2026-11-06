# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Row displaying a metadata."""

from gi.repository import Adw, GObject, Gtk
from metadatacleaner import RESOURCE_PATH


@Gtk.Template(resource_path=RESOURCE_PATH + "/ui/MetadataDetailsRow.ui")
class MetadataDetailsRow(Adw.ActionRow):
    """Row displaying a metadata."""

    __gtype_name__ = "MetadataDetailsRow"

    key = GObject.Property(type=str, default="")
    value = GObject.Property(type=str, default="")
