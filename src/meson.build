# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

configure_file(
  input: 'metadata-cleaner.in',
  output: meson.project_name(),
  configuration: bin_config,
  install_dir: bindir,
  install: true,
  install_mode: 'r-xr-xr-x'
)

sources = [
  '__init__.py',
  'app.py',
]
install_data(sources, install_dir: moduledir)

subdir('modules')
subdir('ui')
