# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

# This Windows port intentionally ships no Linux desktop integration:
# .desktop entries, AppStream metadata and D-Bus activation files are
# excluded. Only the GResource bundle, GSettings schema and icons are needed.

gnome.compile_resources(
  APP_ID,
  APP_ID + '.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

install_data(
  APP_ID + '.gschema.xml',
  install_dir: join_paths(
      get_option('prefix'),
      get_option('datadir'),
      'glib-2.0',
      'schemas',
  ),
)

glib_compile_schemas_exe = find_program('glib-compile-schemas', required: false)
if glib_compile_schemas_exe.found()
  test('Validate schema file',
    glib_compile_schemas_exe,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

scalable_dir = join_paths('hicolor', 'scalable', 'apps')
icon_name_template = '@0@.svg'
if devel
  icon_name_template = '@0@.Debug.svg'
endif

install_data(
  join_paths('icons', (icon_name_template).format(APP_ID)),
  install_dir: join_paths(get_option('datadir'), 'icons', scalable_dir),
  rename: APP_ID + '.svg',
)

symbolic_dir = join_paths('hicolor', 'symbolic', 'apps')
install_data(
  join_paths('icons', ('@0@-symbolic.svg').format(APP_ID)),
  install_dir: join_paths(get_option('datadir'), 'icons', symbolic_dir)
)
