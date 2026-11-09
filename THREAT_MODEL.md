# Threat model

Metadata Cleaner for Windows handles potentially sensitive files and runs
third-party parsing and cleaning tools. This document describes the boundaries
that the project is designed around.

## Assets

- The contents and metadata of the user's files.
- The integrity of the installed application and its updates.
- The user's trust that a downloaded release came from this repository.

## Threats and mitigations

| Threat | Mitigation |
|---|---|
| A file leaves the machine | All parsing and cleaning is local. The application has no upload path; the only network operation is the optional GitHub release check. |
| A downloaded update is replaced | Releases publish SHA-256 sidecars and `SHA256SUMS.txt`; the updater verifies the downloaded installer before launching it. SignPath signing is planned for authenticity. |
| A compromised GitHub token publishes a release | Releases are built by CI from tagged commits; production signing requires a fresh manual approval. MFA is required for repository and SignPath access. |
| A malicious input file exploits a parser | The app uses maintained third-party parsers and isolates cleaning failures per file; a malformed file becomes an error, not a crash of the whole batch. |
| The installer silently changes the system | Inno Setup installs per-user by default, creates normal shortcuts and an uninstaller, and does not install services or drivers. |
| Sensitive data appears in logs | The application logs filenames and error messages, not file contents. Users should remove personal paths before sharing logs publicly. |
| Supply-chain compromise of dependencies | Dependencies are pinned and documented; releases are built in public CI; dependency and code-scanning automation is part of the repository. |

## Out of scope

- A compromised operating system, kernel or user account.
- A user running an installer obtained outside the official Releases page.
- Guarantees that every metadata field, watermark or derived signal can be
  removed. Metadata removal is best-effort.
- An attacker who already has code execution on the machine.

## Reporting

Report suspected vulnerabilities privately as described in
[`SECURITY.md`](SECURITY.md). Do not include private files; use synthetic
samples where possible.
