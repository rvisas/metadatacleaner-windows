# SPDX-FileCopyrightText: Metadata Cleaner contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later

.PHONY: all potfiles xgettext precommit reuse test

all:
	meson setup builddir --prefix=/usr -Ddevel=true && meson compile -C builddir/

install: all
	meson install -C builddir

test:
	meson test -C builddir

potfiles:
	echo "# SPDX-FileCopyrightText: Metadata Cleaner contributors\n# SPDX-License-Identifier: GPL-3.0-or-later\n" > po/POTFILES
	find ./ -not -path '*/.*' -type f -name "*.in" | sort >> po/POTFILES
	echo "" >> po/POTFILES
	find ./ -not -path '*/.*' -type f -name "*.ui" -exec grep -l "translatable=\"yes\"" {} \; | sort >> po/POTFILES
	echo "" >> po/POTFILES
	find ./ -not -path '*/.*' -type f -name "*.py" -exec grep -l "_(\"" {} \; | sort >> po/POTFILES

xgettext:
	xgettext --files-from=po/POTFILES --output=po/io.gitlab.metadatacleaner.metadatacleaner.pot --from-code=UTF-8 --add-comments --keyword=_ --keyword=C_:1c,2

precommit:
	pre-commit run --all-files

reuse-annotate:
	lint_output="$$(reuse lint --lines || true)"; \
	if [ -n "$$lint_output" ]; then \
		echo "$$lint_output"; \
		echo "$$lint_output" | awk -F: '{ print $$1 }' | while read -r file; do \
			reuse annotate \
                --copyright "Metadata Cleaner contributors" \
                --exclude-year \
                --license "GPL-3.0-or-later" \
                --fallback-dot-license \
                "$$file"; \
		done; \
	fi
