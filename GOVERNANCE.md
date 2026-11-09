# Governance

## Project model

Metadata Cleaner for Windows is a single-maintainer, GPL-3.0-or-later,
community port. It is not affiliated with or endorsed by the upstream Metadata
Cleaner maintainers.

## Roles

| Role | Member | Responsibilities |
|---|---|---|
| Author / committer | [@rvisas](https://github.com/rvisas) | Source, build scripts and documentation changes |
| Reviewer | [@rvisas](https://github.com/rvisas) | Review changes from non-committers before merge |
| Release approver | [@rvisas](https://github.com/rvisas) | Approve production signing requests and releases |

The same person currently holds all roles. If additional maintainers join, the
roles must be separated or explicitly documented here, and the SignPath
approver must be a team member trusted to approve a release.

## Decisions

- Changes are proposed through a pull request or issue.
- Port-only changes follow [`docs/versioning.md`](docs/versioning.md); the
  upstream version is never advanced for a port-only fix.
- A release is created from a reviewed commit by a tag or the Release workflow.
- A signed release requires a fresh approval; an earlier approval does not
  authorize later binaries.
- Security reports are handled privately under [`SECURITY.md`](SECURITY.md).

## Signing and release security

- MFA is required on GitHub and on the SignPath account.
- API tokens and signing credentials live in GitHub Actions secrets or the
  signing provider's vault, never in the repository.
- The release workflow must build from the public source tree; prebuilt
  binaries are not uploaded by hand.
- The project does not use multiple free signing identities concurrently.

## Changes to this document

Material changes to roles, signing authority or release approval are reviewed
and committed before the next signing request. This document is versioned with
the source.
