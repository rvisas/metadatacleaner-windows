# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

xdg_config = configuration_data()
xdg_config.set('bindir', bindir)

gnome.compile_resources(
  APP_ID,
  APP_ID + '.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

desktop_file = i18n.merge_file(
  type: 'desktop',
  input: configure_file(
    input: APP_ID + '.desktop.in',
    output: APP_ID + '.desktop.in',
    configuration: xdg_config,
  ),
  output: APP_ID + '.desktop',
  po_dir: join_paths(meson.project_source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

# Validate Desktop file
desktop_file_validate_exe = find_program('desktop-file-validate', required: false)
if desktop_file_validate_exe.found()
  test('Validate desktop file',
    desktop_file_validate_exe,
    args: [desktop_file]
  )
endif

metainfo_file = i18n.merge_file(
  input: APP_ID + '.metainfo.xml',
  output: APP_ID + '.metainfo.xml',
  type: 'xml',
  po_dir: join_paths(meson.project_source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

# Validate MetaInfo file
appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test(
      'Validate appstream file',
      appstream_util,
      args: ['validate-relax', '--nonet', metainfo_file],
  )
endif

configure_file(
  input: APP_ID + '.service.in',
  output: APP_ID + '.service',
  configuration: xdg_config,
  install_dir: dbusdir
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
