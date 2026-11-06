# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

pre_commit_exe = find_program('pre-commit', required: false)
if pre_commit_exe.found()
  test(
    'Check typing, code style, docstrings, reuse',
    pre_commit_exe,
    args: [
      'run',
      '--all-files'
    ]
  )
endif
