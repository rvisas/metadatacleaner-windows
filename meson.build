# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

project(
  'metadata-cleaner',
  version: '4.0.1.1',
  license: ['GPL-3.0-or-later', 'CC-BY-SA-4.0'],
  meson_version: '>= 0.59.0'
)

APP_ID = 'io.gitlab.metadatacleaner.metadatacleaner'

gnome = import('gnome')
i18n = import('i18n')

prefix = get_option('prefix')
bindir = prefix / get_option('bindir')
datadir = prefix / get_option('datadir')
localedir = prefix / get_option('localedir')
dbusdir = datadir / 'dbus-1' / 'services'

devel = get_option('devel')
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'metadatacleaner')

bin_config = configuration_data()
bin_config.set('localedir', localedir)
bin_config.set('pkgdatadir', pkgdatadir)
bin_config.set('app_id', APP_ID)
bin_config.set('devel', devel ? 'True' : 'False')
bin_config.set('version', meson.project_version())

if devel
  git = find_program('git')
  if git.found()
    branch = run_command('git', 'branch', '--show-current', check: true).stdout().strip()
    revision = run_command('git', 'rev-parse', '--short', 'HEAD', check: true).stdout().strip()
    version = '@0@-@1@'.format(branch, revision)
    bin_config.set('VERSION', version)
  endif
endif

subdir('data')
subdir('src')
subdir('po')
subdir('tests')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true
)
