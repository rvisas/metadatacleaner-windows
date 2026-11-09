# Repository standards

This document explains the structure choices for this repository. It is based
on a review of open-source projects that are listed on the SignPath Foundation
projects page and on common practices in high-visibility GitHub repositories.

## How the comparison was made

1. Read the official SignPath Foundation conditions:
   <https://signpath.org/terms.html>.
2. Listed the projects published at <https://signpath.org/projects.html>.
3. Extracted the public GitHub repository for each project and ranked them by
   GitHub stars with the GitHub API.
4. Compared the root layout, `.github/` configuration, documentation and
   release/security automation of the highest-star projects.

The highest-star projects in that snapshot included OpenCode, Orca, Starship,
ImHex, pandoc, Sniffnet, Kazumi, Folo, VSCodium and Flameshot. Star counts change
constantly; the important pattern is the structure, not the exact ranking.

## Patterns worth adopting

High-visibility projects consistently provide:

- a short README with a clear product name, tagline, download CTA and status;
- a recognized OSI license and explicit third-party attribution;
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md` and
  issue/PR templates;
- a changelog and a documented versioning/release process;
- CI that runs tests on every change, plus security analysis and dependency
  updates;
- release automation that builds from a tag, publishes checksums and records
  provenance;
- a code signing policy and a privacy policy when the product handles user
  files;
- `CODEOWNERS` and a documented decision/roles model;
- documentation under `docs/`, not only in the README.

High-star projects often also have a roadmap, a threat model or incident
response policy, author/contributor files, and a citation file. Those are
useful when the project handles security-sensitive data; they are included
here for that reason.

## What this repository now includes

| Area | File or workflow |
|---|---|
| Product and download | `README.md`, `DOWNLOAD.md` |
| License and attribution | `LICENSE`, `LICENSE.md`, `LICENSES/`, `AUTHORS.md` |
| Contributing and conduct | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `AGENTS.md` |
| Support and governance | `SUPPORT.md`, `GOVERNANCE.md`, `CODEOWNERS` |
| Security | `SECURITY.md`, `THREAT_MODEL.md`, `INCIDENT_RESPONSE.md`, CodeQL |
| Privacy and signing | `PRIVACY.md`, `CODE_SIGNING_POLICY.md`, `docs/code-signing.md` |
| Release discipline | `CHANGELOG.md`, `CITATION.cff`, `docs/versioning.md`, provenance attestation |
| Documentation | `docs/architecture.md`, `docs/build.md`, `docs/releasing.md`, `docs/upstream.md`, `docs/signpath-application.md` |
| Tests | `tests/` unit, static and runtime payload tests |
| Automation | tests, release, CodeQL and Dependabot |

## Deliberate differences

- **No Linux packaging.** The port is Windows-only by design; `.desktop`,
  AppStream and D-Bus files are excluded and tested against.
- **Only English and Spanish UI.** The product ships two interface languages;
  English is the documentation and source language.
- **No Microsoft Store/MSIX.** The chosen distribution and signing route is the
  Inno Setup installer with SignPath Foundation.
- **No inflated claims.** The project is an early-stage port. The repository
  does not claim stars, downloads or media coverage that it does not have.

## Remaining gaps

- SignPath approval and the actual signing configuration are pending.
- The project has little external adoption or independent coverage, which is
  the weakest part of a SignPath reputation review.
- Branch protection and required reviewers are repository settings, not files;
  they should be enabled after the maintainer confirms the workflow.
- A fully reproducible payload build is documented but not yet verified
  bit-for-bit across machines.
