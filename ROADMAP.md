# Roadmap

This is a direction document, not a promise of dates or scope. Priorities may
change after a security report or an upstream release.

## Near term

- Complete the SignPath Foundation application and sign the launcher,
  installer and uninstaller.
- Keep the Windows delta small enough to reapply to new upstream releases.
- Continue measuring folder-import and metadata-inspection performance on
  large collections.
- Expand runtime coverage for PDF, DOCX, MP4 and archive cleaning.
- Improve keyboard navigation and screen-reader labeling in the GTK UI.
- Document troubleshooting for SmartScreen and unsigned preview builds.

## Later

- Evaluate additional image and video formats supported by mat2.
- Improve update-channel diagnostics when a release has no checksum sidecar.
- Add reproducible-build checks for the packaged payload.
- Consider a portable distribution in addition to the per-user installer.

## Out of scope

- Linux desktop integration, Flatpak, AppStream and D-Bus packaging. The
  Windows port intentionally excludes them.
- Microsoft Store/MSIX distribution. The chosen channel is the Inno Setup
  installer and SignPath Foundation signing.
- Translating the product name. `Metadata Cleaner` remains a proper noun.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SUPPORT.md`](SUPPORT.md) and
[`GOVERNANCE.md`](GOVERNANCE.md).
