# SignPath Foundation application

This page maps the live SignPath Foundation application form to this
repository. It is a preparation aid, not a submitted application.

Official form: <https://signpath.org/apply.html>

Official conditions: <https://signpath.org/terms.html>

## Field-by-field answers

| Form field | Required | Value for this project |
|---|---|---|
| Project Name | Yes | `Metadata Cleaner for Windows` |
| Repository URL | Yes | `https://github.com/rvisas/metadatacleaner-windows` |
| Homepage URL | Yes | `https://github.com/rvisas/metadatacleaner-windows` |
| Download URL | No | `https://github.com/rvisas/metadatacleaner-windows/blob/main/DOWNLOAD.md` |
| Privacy Policy URL | No | `https://github.com/rvisas/metadatacleaner-windows/blob/main/PRIVACY.md` |
| Wikipedia URL | No | Leave blank; there is no article. |
| Tagline | Yes | `A Windows port of Metadata Cleaner that removes file metadata locally before you share a file.` |
| Category | Yes | `Productivity` |
| Description | Yes | See below. |
| Reputation | Yes | See below; this is currently the weakest field. |
| Maintainer Type | No | `Individual maintainer(s)` |
| Build System | Yes | `GitHub Actions` |
| First Name / Last Name | Yes | Your legal or preferred account name. |
| Email | Yes | An address you monitor; SignPath sends review questions there. |
| Company Name | No | Leave blank unless applying through an employer. |
| Primary Discovery Channel | Yes | Choose the truthful source, for example `AI / LLM tools` or `Organic search`. |
| Exact source | No | Add the actual source if you have one. |
| Code of Conduct consent | Yes | Must be checked by the applicant. |
| Data-processing consent | Yes | Must be checked by the applicant. |

The form also displays the Code of Conduct and SignPath Foundation certificate
terms. Read them before submitting. Certificates are issued in SignPath
Foundation's name and can be revoked if the terms are violated.

## Description

> Metadata Cleaner for Windows is an unofficial Windows port of the Metadata
> Cleaner application. It lets users inspect and remove metadata from files
> locally before sharing them, with a native desktop interface and a standard
> Windows installer built from this public repository.

## Reputation

Write only verifiable facts. At the time of writing, the repository is an
early-stage port, not a widely adopted product:

- Upstream project: <https://gitlab.com/metadatacleaner/metadatacleaner>
  (maintained; release `v4.0.1` published 2026-11-01).
- This repository is a public, tagged port with repeated releases and a public
  CI history:
  <https://github.com/rvisas/metadatacleaner-windows/releases>
- Build and test history:
  <https://github.com/rvisas/metadatacleaner-windows/actions>
- The source, build instructions, patches, tests, privacy policy and code
  signing policy are public.

Do not invent stars, download counts, media coverage or user numbers. If the
project has no independent coverage yet, say so; SignPath can evaluate the
quality of the repository, but it may decline an application that lacks
external traction.

## Pre-application checklist

- [x] Public repository.
- [x] OSI-approved license: `GPL-3.0-or-later`.
- [x] README explains the product, platform and download location.
- [x] Releases are built by the public GitHub Actions workflow.
- [x] A released installer exists.
- [x] `CODE_SIGNING_POLICY.md` contains the required SignPath statement and
  roles.
- [x] `PRIVACY.md` describes local processing and the update check.
- [x] `DOWNLOAD.md` mentions SignPath Foundation and the current unsigned state.
- [x] No proprietary components are part of the project source.
- [x] No telemetry or file uploads.
- [x] Installer and launcher carry product/version metadata.
- [ ] Maintainer's GitHub account has MFA enabled.
- [ ] SignPath account MFA will be enabled after the account is created.
- [ ] A review of the fork/upstream relationship is accepted by SignPath.

## Before you submit

1. Enable MFA on GitHub.
2. Confirm the Download URL and Privacy Policy URL open without a login.
3. Make sure the latest release page links to the code signing policy.
4. Submit the form with honest reputation information.
5. Do not claim that the project is already signed until SignPath approves it
   and a signature is visible on the installer.
