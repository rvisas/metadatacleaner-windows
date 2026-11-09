## Summary

Describe the user-visible change and why it is needed.

## Tests

- [ ] Full local suite passes (`python -m unittest discover -s tests -v`)
- [ ] `python -m compileall -q src tests`
- [ ] `python scripts/versioning.py check`
- [ ] `python scripts/check_docs.py`
- [ ] `git diff --check` is clean
- [ ] No build output, installer or cache is tracked

## Versioning and release

- [ ] Port-only change: version bumped in the last component (for example
      `4.0.1.7` → `4.0.1.7`)
- [ ] Upstream change: base confirmed against upstream and port revision reset
      to `.1`
- [ ] Documentation updated for commands, paths or versions that changed

## Notes

Add screenshots, logs or manual test steps when relevant.
