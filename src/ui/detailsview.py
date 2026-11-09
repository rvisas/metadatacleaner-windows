# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""View details of a file."""

from gettext import gettext as _

from gi.repository import Adw, Gtk
from metadatacleaner import RESOURCE_PATH
from metadatacleaner.modules.file import File, FileState
from metadatacleaner.ui.metadataview import MetadataView


@Gtk.Template(resource_path=RESOURCE_PATH + "/ui/DetailsView.ui")
class DetailsView(Adw.Bin):
    """View details of a file."""

    __gtype_name__ = "DetailsView"

    def __init__(self, *args, **kwargs) -> None:
        """Details view initialization."""
        super().__init__(*args, **kwargs)
        self.clear()

    def view_file(self, f: File) -> None:
        """Set the file to view.

        Args:
            f (File): The file to view.
        """
        self.set_child(None)
        if f.state == FileState.HAS_METADATA:
            self._setup_metadata_details(f)
        elif f.state == FileState.CLEANED:
            self._setup_cleaned_details()
        elif f.state in [
            FileState.ERROR_WHILE_CHECKING_METADATA,
            FileState.ERROR_WHILE_INITIALIZING,
            FileState.ERROR_WHILE_REMOVING_METADATA,
            FileState.HAS_NO_METADATA,
            FileState.UNSUPPORTED,
        ]:
            self._setup_error_details(f)

    def set_content(self, w) -> None:
        """Set the widget's child."""
        self.set_child(w)

    def _setup_cleaned_details(self) -> None:
        self.set_content(
            Adw.StatusPage(
                # translators: side panel message when selecting a file that
                #              has been cleaned
                title=_("The File Has Been Cleaned"),
                description=_(
                    # translators: side panel subtitle when selecting a file
                    #              that has been cleaned. The limitations can
                    #              be viewed by clicking a button below it
                    "Known metadata have been removed, however the cleaning "
                    "process has some limitations."
                ),
                child=Gtk.Button(
                    # translators: button that shows more info about the
                    #              cleaning process, it's shown below a
                    #              label that gives it context
                    label=_("Learn more"),
                    action_name="win.info",
                    halign=Gtk.Align.CENTER,
                    css_classes=["pill", "suggested-action"],
                ),
                css_classes=["compact"],
            )
        )

    def _setup_metadata_details(self, f: File) -> None:
        self.set_content(MetadataView(metadata=f.metadata))

    def _setup_error_details(self, f: File) -> None:
        info_titles = {
            # translators: error shown on the side panel when selecting
            #              a file
            FileState.ERROR_WHILE_INITIALIZING: _("Unable to Read the File"),
            # translators: error shown on the side panel when selecting
            #              a file
            FileState.UNSUPPORTED: _("File Type not Supported"),
            FileState.ERROR_WHILE_CHECKING_METADATA: _(
                # translators: error shown on the side panel when selecting
                #              a file
                "Unable to Check for Metadata"
            ),
            # translators: error shown on the side panel when selecting
            #              a file
            FileState.HAS_NO_METADATA: _("No Known Metadata"),
            FileState.ERROR_WHILE_REMOVING_METADATA: _(
                # translators: error shown on the side panel when
                #              selecting a file
                "Unable to Remove Metadata"
            ),
        }
        info_details = str(f.error or "")
        if f.state == FileState.HAS_NO_METADATA:
            # translators: message shown on the side panel when selecting a
            #              file that doesn't have known metadata
            info_details = _("The file will be cleaned anyway to be sure.")
        self.set_content(
            Adw.StatusPage(
                title=info_titles[f.state],
                description=info_details,
                css_classes=["compact"],
            )
        )

    def clear(self) -> None:
        """Informs the user that they need to select a file"""
        self.set_content(
            Adw.StatusPage(
                # translators: message shown on the side panel when no file
                #              has been selected
                title=_("Select a file to view its metadata"),
                css_classes=["compact"],
            )
        )
