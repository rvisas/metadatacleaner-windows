<!--
SPDX-FileCopyrightText: Metadata Cleaner contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Contributing

This is an unofficial Windows port. Windows-specific fixes are in scope here;
upstream application behavior should be discussed with the upstream project
first. Read [`AGENTS.md`](AGENTS.md) and [`docs/architecture.md`](docs/architecture.md)
before changing code.

## Languages

The application and installer ship **English and Spanish only**. English is the
source language; Spanish lives in `po/es.po`. **Metadata Cleaner is a proper
noun and must never be translated.** Do not add another catalog unless the
installer language list is intentionally changed too. Do not add Linux desktop,
Flatpak, Flathub, AppStream or D-Bus files; the Windows build does not use them.

## Code

The application source is under `src/`. Before writing code, open an issue to
discuss the change. Keep the Windows delta small and reviewable: prefer a
guarded Windows branch over a large rewrite, and document patches in
[`docs/upstream.md`](docs/upstream.md).

### Conventions

- Python 3, PEP 8, PEP 257 docstrings and PEP 484 type hints.
- File and directory names are English; Python identifiers and comments are
  English.
- UI strings are English in source and translated in `po/es.po`.
- No build output, installers, caches or downloaded updates in the repository.

Run the suite from the repository root:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
git diff --check
```

Optional local hooks:

```bash
pip install pre-commit
pre-commit run --all-files
```

### New files

If you add a UI or Python file, add its path to the appropriate
`data/*.gresource.xml` or `src/**/meson.build` file. If it contains translatable
text, add the string to `po/es.po` and run the localization tests.

### Licenses and copyright notices

Add an SPDX header to every new file, or a separate `original-file.ext.license`
file, following the [SPDX specification](https://spdx.dev/):

```text
SPDX-FileCopyrightText: 2026 <contributor>
SPDX-License-Identifier: GPL-3.0-or-later
```

### Commit messages

Use an imperative English subject. For example:

```text
Folder import: request type attributes from GIO
```

Describe user-visible changes and tests in the body when useful.

## Versioning

Port-only fixes increment the last component (`4.0.1.4` → `4.0.1.5`). Never
invent a new upstream component for a port change. See
[`docs/versioning.md`](docs/versioning.md).
