# Code signing on Windows

This project publishes a Win32 Inno Setup installer, not an MSIX package. The
chosen signing route is the **SignPath Foundation** open-source programme.
Microsoft Store and MSIX distribution are explicitly out of scope for this
repository.

This document records the signing plan, the application requirements and the
release flow. It is not a claim that the project is already signed: the current
installer is unsigned and releases are pre-releases until SignPath approves the
project.

## Why signing matters

- The installer and launcher show **Unknown publisher** without a trusted
  Authenticode signature.
- SmartScreen may show **Windows protected your PC** on first download.
- A signature proves that the binary came from the publisher and was not
  modified after signing, provided it is timestamped and verified.

A signature does **not** guarantee that SmartScreen is silent immediately.
Since 2024, OV and EV certificates follow the same reputation-building process:
the first downloads of a new file can still warn until Microsoft has enough
telemetry. SignPath Foundation builds reputation across releases signed with
the same certificate.

## Why SignPath Foundation

SignPath Foundation lets an eligible OSS project use a code-signing certificate
issued to the foundation. The private key remains in SignPath's hardware
security module (HSM); the repository and the build machine never hold it.

The trust model is deliberately different from a certificate issued to an
individual:

- SignPath verifies the project and the public repository.
- SignPath verifies that the signed artifact came from a trusted CI build.
- Windows shows **SignPath Foundation** as the publisher, not the maintainer's
  name.
- Every production signing request requires manual approval.

That last point is a feature, not a bug: a compromised GitHub token alone cannot
produce a signed release.

## Eligibility

The official conditions are at <https://signpath.org/terms.html>. For this
repository, the relevant requirements are:

- **OSI-approved license without commercial dual-licensing.** This project is
  GPL-3.0-or-later.
- **No malware or potentially unwanted programs.** The application removes
  metadata locally; it has no telemetry, uploads, credential collection or
  security-circumvention features.
- **No proprietary components.** All project source and build scripts are
  public. Bundled third-party runtimes keep their own OSS licenses.
- **Maintained and released.** The repository has tagged releases and a public
  build workflow.
- **Documented.** The README describes the product, supported platforms and
  download location.
- **Verifiable builds.** GitHub Actions builds the payload and installer from
  the tagged source tree. Prebuilt binaries are not uploaded by hand.
- **MFA and signing roles.** The maintainer must enable MFA on GitHub and
  SignPath, and the project must name authors, reviewers and approvers.
- **Code signing policy on the project home page.** The exact phrase and the
  required role/privacy information are in the repository README and in
  [`CODE_SIGNING_POLICY.md`](../CODE_SIGNING_POLICY.md).
- **Privacy policy.** See [`PRIVACY.md`](../PRIVACY.md). The application does
  not upload files; the optional update check contacts GitHub only.

### Fork-specific risk

SignPath's terms allow a modified upstream project only when the fork is
visibly based on upstream, the release branches follow upstream, and the
project satisfies the review and approval rules. This repository is an
unofficial Windows port built from the upstream source tree plus documented
patches. The application should describe that relationship plainly and let
SignPath decide eligibility; approval is not guaranteed.

## Application process

### 1. Prepare the repository

Before applying, make sure the public repository contains:

- `LICENSE` at the root and SPDX headers on source files;
- a README that explains what the application does and where releases are
  downloaded;
- a `Code signing policy` section with the exact SignPath phrase, team roles
  and a privacy-policy link;
- public GitHub Actions workflows that build the release artifacts;
- at least one downloadable release in the form that should be signed;
- MFA enabled on the maintainer's GitHub account.

The repository already contains these items. The signing policy and privacy
policy are versioned with the source so reviewers can inspect them.

### 2. Submit the application

Open <https://signpath.org/apply.html> and complete the form. The form is an
embedded HubSpot form; the exact labels can change, but it asks for the
following information:

| Field | What to provide for this project |
|---|---|
| Project name | `Metadata Cleaner for Windows` |
| Repository URL | `https://github.com/rvisas/metadatacleaner-windows` |
| Project website/download page | The GitHub Releases page |
| License | `GPL-3.0-or-later` (OSI-approved) |
| Project description | Unofficial Windows port of Metadata Cleaner; GTK4/PyGObject; built with MSYS2 UCRT64 and GitHub Actions; one Inno Setup installer for Windows 10/11 x64 |
| Maintainer contact | An address you monitor; SignPath may ask follow-up questions |
| Code signing policy URL | `https://github.com/rvisas/metadatacleaner-windows/blob/main/CODE_SIGNING_POLICY.md` |
| Privacy policy URL | `https://github.com/rvisas/metadatacleaner-windows/blob/main/PRIVACY.md` |
| Build system | GitHub Actions, public workflow `.github/workflows/release.yml` |
| Artifacts to sign | `MetadataCleaner.exe`, the Inno Setup installer and the uninstaller |

Keep the description factual. Do not claim that the project is affiliated with
the upstream maintainers; it is an unofficial port.

### 3. Review and approval

SignPath reviews the repository, the release process, the signing policy and
the project's public reputation. Reviewers may ask for clarification by email.

**There is no published approval SLA.** Public reports from OSS maintainers
range from roughly one week to more than a month; some applications are
declined or asked to reapply after gaining more public traction. Plan the
release schedule so signing is not on the critical path, and do not promise
users a signed build on a specific date.

Approval is discretionary. SignPath Foundation is not a certificate authority
and does not issue certificates in the maintainer's name; it accepts projects
that it is willing to vouch for.

### 4. Onboarding after approval

After approval, SignPath provides access to an organization and project. The
maintainer then configures:

1. **GitHub integration** — install the SignPath GitHub App for the public
   repository.
2. **Trusted build system** — GitHub Actions, the repository and the release
   tag/workflow pattern (for example `refs/tags/v*-windows`).
3. **Artifact configuration** — the files to sign, with product-name and
   product-version metadata restrictions. The launcher, installer and
   uninstaller must carry consistent product metadata.
4. **Signing policy** — a production policy such as `release-signing`, with
   manual approval required for every release.
5. **Roles** — authors, reviewers and approvers. This repository currently has
   one maintainer, so the same person holds the roles; the policy still records
   them explicitly.
6. **API credentials** — create a SignPath API token and store it as the
   GitHub Actions secret `SIGNPATH_API_TOKEN`; store the organization ID as a
   repository variable. Never commit either value.

The exact slugs and action version are shown in the SignPath project's CI
integration page. They are project-specific and must not be guessed.

## Release flow

The signing step is intentionally separated from the build step:

1. A tag `v<version>-windows` starts the release workflow.
2. The workflow builds the payload and installer on a GitHub-hosted runner.
3. It verifies the installer and uploads the unsigned artifacts.
4. A signing job submits the artifacts to SignPath with the trusted-build
   origin information.
5. The approver reviews the origin, test results and version, then approves the
   request in SignPath.
6. The signed artifacts are downloaded, checked with `signtool verify /pa`, and
   attached to the GitHub Release together with the SHA-256 sidecars.

The SignPath action's default wait for approval is too short for a human
reviewer. The workflow must allow a realistic timeout (for example one hour)
and keep the unsigned build artifact available so a missed approval can be
retried without rebuilding.

Every production release requires a fresh approval. A previous approval does
not authorize later binaries.

## What gets signed

| Artifact | Why |
|---|---|
| `MetadataCleaner.exe` | Native launcher the user runs |
| `MetadataCleaner-<version>-windows-x64-setup.exe` | Installer downloaded from Releases |
| `unins000.exe` | Uninstaller; Inno Setup signs it with `SignedUninstaller=yes` |

Bundled dependencies (GTK, Python, exiftool, ffmpeg and their DLLs) keep their
own signatures and licenses. SignPath signs this project's own artifacts, not
upstream binaries.

## Code signing policy

The public policy is in [`CODE_SIGNING_POLICY.md`](../CODE_SIGNING_POLICY.md).
It contains the exact statement required by SignPath:

> Free code signing provided by SignPath.io, certificate by SignPath Foundation.

It also names the project roles, links the privacy policy and states which
artifacts are covered.

## If SignPath declines

Do not collect multiple free signing identities concurrently. Use one of these
fallbacks:

1. **OSSign** — free for qualifying OSS when its application queue is open;
   it uses a different signing identity and reputation.
2. **Certum Open Source Code Signing** — paid, but issued in the maintainer's
   name as "Open Source Developer".
3. **Azure Artifact Signing** (formerly Trusted Signing) — paid subscription;
   availability depends on the maintainer's country.
4. **OV/EV certificate** — paid; standard commercial route, with reputation
   building rather than an instant SmartScreen bypass.

Sigstore/cosign is useful for provenance and Linux/container artifacts, but it
is not an Authenticode trust path for a Windows `.exe`. A self-signed
certificate is for development or enterprise-managed deployment only.

## Verification

After signing, verify the downloaded installer on Windows:

```powershell
signtool verify /pa /v .\MetadataCleaner-<version>-windows-x64-setup.exe
Get-AuthenticodeSignature .\MetadataCleaner-<version>-windows-x64-setup.exe |
  Format-List Status, StatusMessage, SignerCertificate
```

The expected signer is **SignPath Foundation**. A valid signature does not
replace the SHA-256 check: verify both.

## Current status

- Releases are marked **pre-release** while unsigned.
- SHA-256 sidecars and `SHA256SUMS.txt` are published for manual verification.
- The application verifies the SHA-256 of downloaded updates before running
  them.
- Do not describe the installer as signed until the file properties show a
  valid Authenticode signature and `signtool verify /pa` succeeds.
