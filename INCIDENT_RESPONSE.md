# Incident response

This document covers security or integrity incidents that affect a released
build, the update path or the signing configuration.

## Reporting

Use GitHub's private vulnerability reporting as described in
[`SECURITY.md`](SECURITY.md). Do not open a public issue while a report is under
investigation.

## Triage

1. Acknowledge the report and preserve the evidence.
2. Identify affected versions, release assets and platforms.
3. Determine whether the issue is a false positive, a documentation issue, a
   code defect or a compromised build/release.
4. If a release or signing credential may be compromised, pause new releases
   and notify the signing provider before publishing details.

## Containment and fix

- Remove or mark affected release assets as withdrawn.
- Build and test a fix from a reviewed commit.
- Publish a new port revision; never replace a released installer in place.
- If signing was involved, ask the signing provider to revoke or suspend the
  affected signing request/certificate as appropriate.

## Disclosure

- Publish a concise advisory after users can update, or earlier if active
  exploitation requires it.
- Include affected versions, fixed version, impact and verification guidance.
- Credit the reporter unless they ask to remain anonymous.

## Follow-up

- Add a regression test or guardrail when the cause can be tested.
- Update `THREAT_MODEL.md`, `SECURITY.md` or the release process if the
  incident exposed a gap.
- Record the timeline and decisions in the advisory or release notes without
  including private user data.
