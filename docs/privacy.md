# Privacy policy

Metadata Cleaner for Windows is a local desktop application. It does not
require an account and does not collect telemetry, analytics or usage data.

## Files

Files you add are read and, when you request cleaning, written on your own
computer. Their contents are never uploaded. The application may create a
temporary copy while cleaning; the copy is removed after the original is
replaced.

## Network access

The application has one optional network operation: checking GitHub Releases
for a newer Windows installer.

- The check requests the public release metadata from `api.github.com`.
- It sends the standard HTTP request information needed to reach GitHub; it does
  not send file contents, file names, metadata or a user identifier.
- Automatic checks can be disabled in **Settings**. A manual check is started
  only when the user selects **Check for Updates…**.
- If the user chooses to update, the installer is downloaded from the GitHub
  release and its SHA-256 is verified before it is launched.

The installer itself contains no telemetry. Bundled third-party components
(GTK, Python, exiftool, ffmpeg, mat2) do not contact the network unless the
application explicitly invokes them for a local file operation.

## Data retention

The application does not maintain a server-side account or database. Settings,
the selected language and the last update-check timestamp are stored locally
in the user's Windows profile. Uninstalling removes the application; local
settings may remain in the user profile unless removed manually.

## Contact

Privacy questions can be opened at
<https://github.com/rvisas/metadatacleaner-windows/issues>.

This project is an unofficial Windows port and is not affiliated with the
upstream Metadata Cleaner maintainers.
