.PHONY: build dev

PYTHON?=python3
PYTHON_INTERPRETER?=$(PYTHON)
MODULE:=quake
DESTDIR:=/
PREFIX?=/usr/local
exec_prefix:=$(PREFIX)
bindir = $(exec_prefix)/bin

# Use site.getsitepackages([PREFIX]) to guess possible install paths for uninstall.
PYTHON_SITEDIRS_FOR_PREFIX="env PREFIX=$(PREFIX) $(PYTHON_INTERPRETER) scripts/all-sitedirs-in-prefix.py"
ROOT_DIR=$(shell pwd)
DATA_DIR=$(ROOT_DIR)/quake/data
COMPILE_SCHEMA:=1

datarootdir:=$(PREFIX)/share
datadir:=$(datarootdir)
localedir:=$(datarootdir)/locale
gsettingsschemadir:=$(datarootdir)/glib-2.0/schemas

AUTOSTART_FOLDER:=~/.config/autostart

DEV_DATA_DIR:=$(DATA_DIR)

SHARE_DIR:=$(datadir)/quake
QUAKE_THEME_DIR:=$(SHARE_DIR)/quake
LOGIN_DESTOP_PATH = $(SHARE_DIR)
IMAGE_DIR:=$(SHARE_DIR)/pixmaps
GLADE_DIR:=$(SHARE_DIR)
SCHEMA_DIR:=$(gsettingsschemadir)

SLUG:=fragment_name

default: prepare-install
	# 'make' target, so users can install quake without need to install the 'dev' dependencies

prepare-install: generate-desktop generate-paths generate-mo compile-glib-schemas-dev

reset:
	dconf reset -f /org/quake/


all: clean dev style checks dists test docs

dev: clean-ln-venv ensure-pip pipenv-install-dev requirements ln-venv setup-githook \
	 prepare-install install-dev-locale
dev-actions: ensure-pip-system pipenv-install-dev prepare-install

ensure-pip:
	./scripts/bootstrap-dev-pip.sh

ensure-pip-system:
	./scripts/bootstrap-dev-pip.sh system

dev-no-pipenv: clean
	virtualenv --python $(PYTHON_INTERPRETER) .venv
	. .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt -e .

pipenv-install-dev:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv install --dev --python $(PYTHON_INTERPRETER)

ln-venv:
	# use that to configure a symbolic link to the virtualenv in .venv
	rm -rf .venv
	ln -s $$(pipenv --venv) .venv

clean-ln-venv:
	@rm -f .venv

install-system: install-schemas compile-shemas install-locale install-quake

install-quake:
	# you probably want to execute this target with sudo:
	# sudo make install
	@echo "#############################################################"
	@echo
	@echo "Installing from source on your system is not recommended."
	@echo "Please prefer you application package manager (apt, yum, ...)"
	@echo
	@echo "#############################################################"
	@if [ "$(DESTDIR)" = "" ]; then $(PYTHON_INTERPRETER) -m pip install -r requirements.txt; fi

	# @if [ `python -c "import sys; print(sys.version_info[0])"` -eq 2 ]; then SETUPTOOLS_SCM_PRETEND_VERSION=3.9.0; fi

	# @rm -f quake/paths.py.dev
	# @if [ -f quake/paths.py ]; then mv quake/paths.py quake/paths.py.dev; fi
	# @cp -f quake/paths.py.in quake/paths.py
	# @sed -i -e 's|{{ LOCALE_DIR }}|"$(localedir)"|g' quake/paths.py
	# @sed -i -e 's|{{ IMAGE_DIR }}|"$(IMAGE_DIR)"|g' quake/paths.py
	# @sed -i -e 's|{{ GLADE_DIR }}|"$(GLADE_DIR)"|g' quake/paths.py
	# @sed -i -e 's|{{ QUAKE_THEME_DIR }}|"$(QUAKE_THEME_DIR)"|g' quake/paths.py
	# @sed -i -e 's|{{ SCHEMA_DIR }}|"$(SCHEMA_DIR)"|g' quake/paths.py
	# @sed -i -e 's|{{ LOGIN_DESTOP_PATH }}|"$(LOGIN_DESTOP_PATH)"|g' quake/paths.py
	# @sed -i -e 's|{{ AUTOSTART_FOLDER }}|"$(AUTOSTART_FOLDER)"|g' quake/paths.py

	@$(PYTHON_INTERPRETER) -m pip install . --root "$(DESTDIR)" --prefix="/usr" || echo -e "\033[31;1msetup.py install failed, you may need to run \"sudo git config --global --add safe.directory '*'\"\033[0m"

	@rm -f quake/paths.py
	@if [ -f quake/paths.py.dev ]; then mv quake/paths.py.dev quake/paths.py; fi

	@update-desktop-database || echo "Could not run update-desktop-database, are you root?"
	@rm -rfv build *.egg-info

install-locale:
	for f in $$(find po -iname "*.mo"); do \
		l="$${f%%.*}"; \
		lb=$$(basename $$l); \
		install -Dm644 "$$f" "$(DESTDIR)$(localedir)/$$lb/LC_MESSAGES/quake.mo"; \
	done;

install-dev-locale:
	for f in $$(find po -iname "*.mo"); do \
		l="$${f%%.*}"; \
		lb=$$(basename $$l); \
		install -Dm644 "$$f" "quake/po/$$lb/LC_MESSAGES/quake.mo"; \
	done;

uninstall-locale:
	find $(DESTDIR)$(localedir)/ -name "quake.mo" -exec rm -f "{}" + || :
	# prune two levels of empty locale/ subdirs
	find "$(DESTDIR)$(localedir)" -type d -a -empty -exec rmdir "{}" + || :
	find "$(DESTDIR)$(localedir)" -type d -a -empty -exec rmdir "{}" + || :

uninstall-dev-locale:
	@rm -rf quake/po

install-schemas:
	install -dm755                                       "$(DESTDIR)$(datadir)/applications"
	install -Dm644 "$(DEV_DATA_DIR)/quake.desktop"       "$(DESTDIR)$(datadir)/applications/"
	install -Dm644 "$(DEV_DATA_DIR)/quake-prefs.desktop" "$(DESTDIR)$(datadir)/applications/"
	install -dm755                                       "$(DESTDIR)$(datadir)/metainfo/"
	install -Dm644 "$(DEV_DATA_DIR)/quake.desktop.metainfo.xml"  "$(DESTDIR)$(datadir)/metainfo/"
	install -dm755                                 "$(DESTDIR)$(IMAGE_DIR)"
	install -Dm644 "$(DEV_DATA_DIR)"/pixmaps/*.png "$(DESTDIR)$(IMAGE_DIR)/"
	install -Dm644 "$(DEV_DATA_DIR)"/pixmaps/*.svg "$(DESTDIR)$(IMAGE_DIR)/"
	install -dm755                                     "$(DESTDIR)$(PREFIX)/share/pixmaps"
	install -Dm644 "$(DEV_DATA_DIR)/pixmaps/quake.png" "$(DESTDIR)$(PREFIX)/share/pixmaps/"
	install -dm755                                           "$(DESTDIR)$(SHARE_DIR)"
	install -Dm644 "$(DEV_DATA_DIR)/autostart-quake.desktop" "$(DESTDIR)$(SHARE_DIR)/"
	install -dm755                           "$(DESTDIR)$(GLADE_DIR)"
	install -Dm644 "$(DEV_DATA_DIR)"/*.glade "$(DESTDIR)$(GLADE_DIR)/"
	install -dm755                                         "$(DESTDIR)$(SCHEMA_DIR)"
	install -Dm644 "$(DEV_DATA_DIR)/org.quake.gschema.xml" "$(DESTDIR)$(SCHEMA_DIR)/"

compile-shemas:
	if [ $(COMPILE_SCHEMA) = 1 ]; then glib-compile-schemas $(DESTDIR)$(gsettingsschemadir); fi

uninstall-system: uninstall-schemas uninstall-locale
	$(SHELL) -c $(PYTHON_SITEDIRS_FOR_PREFIX) \
		| while read sitedir; do \
			echo "rm -rf $(DESTDIR)$$sitedir/{quake,quake-*.egg-info}"; \
			rm -rf $(DESTDIR)$$sitedir/quake; \
			rm -rf $(DESTDIR)$$sitedir/quake-*.egg-info; \
		done
	rm -f "$(DESTDIR)$(bindir)/quake"
	rm -f "$(DESTDIR)$(bindir)/quake-prefs"
	rm -f "$(DESTDIR)$(bindir)/quake-toggle"

purge-system: uninstall-system reset

uninstall-schemas:
	rm -f "$(DESTDIR)$(datadir)/applications/quake.desktop"
	rm -f "$(DESTDIR)$(datadir)/applications/quake-prefs.desktop"
	rm -f "$(DESTDIR)$(datadir)/metainfo/quake.desktop.metainfo.xml"
	rm -f "$(DESTDIR)$(datadir)/pixmaps/quake.png"
	rm -fr "$(DESTDIR)$(IMAGE_DIR)"
	rm -fr "$(DESTDIR)$(SHARE_DIR)"
	rm -f "$(DESTDIR)$(SCHEMA_DIR)/org.quake.gschema.xml"
	rm -f "$(DESTDIR)$(SCHEMA_DIR)/gschemas.compiled"

reinstall:
	sudo make uninstall && make && sudo make install && $(DESTDIR)$(bindir)/quake

reinstall-v:
	sudo make uninstall && make && sudo make install && $(DESTDIR)$(bindir)/quake -v

compile-glib-schemas-dev: clean-schemas
	glib-compile-schemas --strict $(DEV_DATA_DIR)

clean-schemas:
	rm -f $(DEV_DATA_DIR)/gschemas.compiled

style:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run pre-commit run --all-files

black:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run black $(MODULE)


checks: black-check flake8 pylint reno-lint

black-check:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run black --check $(MODULE) --extend-exclude $(MODULE)/_version.py

flake8:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run flake8 quake

pylint:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run pylint --rcfile=.pylintrc --output-format=colorized $(MODULE)

sc: style check

dists: update-po requirements prepare-install rm-dists sdist bdist wheels
build: dists

sdist: generate-paths
	export SKIP_GIT_SDIST=1 && PIPENV_IGNORE_VIRTUALENVS=1 pipenv run python setup.py sdist

rm-dists:
	rm -rf build dist

bdist: generate-paths
	# pipenv run python setup.py bdist
	@echo "Ignoring build of bdist package"

wheels: generate-paths
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run python setup.py bdist_wheel

wheel: wheels

run-local: compile-glib-schemas-dev
ifdef V
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run ./scripts/run-local.sh -v
else
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run ./scripts/run-local.sh
endif

run-local-prefs: compile-glib-schemas-dev
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run ./scripts/run-local-prefs.sh

run-fr: compile-glib-schemas-dev
	LC_ALL=fr_FR.UTF8 PIPENV_IGNORE_VIRTUALENVS=1 pipenv run ./scripts/run-local.sh


shell:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv shell


test:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run pytest $(MODULE)

test-actions:
	xvfb-run -a pipenv run pytest $(MODULE)
test-coverage:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run py.test -v --cov $(MODULE) --cov-report term-missing

test-pip-install-sdist: clean-pip-install-local generate-paths sdist
	@echo "Testing installation by pip (will install on ~/.local)"
	pip install --upgrade -vvv --user $(shell ls -1 dist/*.tar.gz | sort | head -n 1)
	ls -la ~/.local/share/quake
	~/.local/bin/quake

clean-pip-install-local:
	@rm -rfv ~/.local/quake
	@rm -rfv ~/.local/bin/quake
	@rm -rfv ~/.local/lib/python3.*/site-packages/quake
	@rm -rfv ~/.local/share/quake

test-pip-install-wheel: clean-pip-install-local generate-paths wheel
	@echo "Testing installation by pip (will install on ~/.local)"
	pip install --upgrade -vvv --user $(shell ls -1 dist/*.whl | sort | head -n 1)
	ls -la ~/.local/share/quake
	~/.local/bin/quake -v

sct: style check update-po requirements test


docs: clean-docs sdist
	cd docs && PIPENV_IGNORE_VIRTUALENVS=1 pipenv run make html

docs-open:
	xdg-open docs/_build/html/index.html

tag-pbr:
	@{ \
		set -e ;\
		export VERSION=$$(PIPENV_IGNORE_VIRTUALENVS=1 pipenv run python setup.py --version | cut -d. -f1,2,3); \
		echo "I: Computed new version: $$VERSION"; \
		echo "I: presse ENTER to accept or type new version number:"; \
		read VERSION_OVERRIDE; \
		VERSION=$${VERSION_OVERRIDE:-$$VERSION}; \
		PROJECTNAME=$$(PIPENV_IGNORE_VIRTUALENVS=1 pipenv run python setup.py --name); \
		echo "I: Tagging $$PROJECTNAME in version $$VERSION with tag: $$VERSION" ; \
		echo "$$ git tag $$VERSION -m \"$$PROJECTNAME $$VERSION\""; \
		git tag $$VERSION -m "$$PROJECTNAME $$VERSION"; \
		echo "I: Pushing tag $$VERSION, press ENTER to continue, C-c to interrupt"; \
		echo "$$ git push upstream $$VERSION"; \
	}
	@# Note:
	@# To sign, need gpg configured and the following command:
	@#  git tag -s $$VERSION -m \"$$PROJECTNAME $$VERSION\""

pypi-publish: build
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run python setup.py upload -r pypi


update:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv update --clear
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv install --dev


lock: pipenv-lock requirements

requirements:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run pipenv_to_requirements

pipenv-lock:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv lock


freeze:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run pip freeze


setup-githook:
	rm -f .git/hooks/post-commit
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run pre-commit install


push:
	git push origin --tags


clean: clean-ln-venv rm-dists clean-docs clean-po clean-schemas clean-py clean-paths uninstall-dev-locale
	@echo "clean successful"

clean-py:
	@pipenv --rm ; true
	@find . -name "*.pyc" -exec rm -f {} \;
	@rm -f $(DEV_DATA_DIR)/quake-prefs.desktop $(DEV_DATA_DIR)/quake.desktop
	@rm -rf .eggs *.egg-info po/*.pot

clean-paths:
	rm -f quake/paths.py quake/paths.py.dev

clean-po:
	@rm -f po/quake.pot
	@find po -name "*.mo" -exec rm -f {} \;

clean-docs:
	rm -rf doc/_build

update-po:
	echo "generating pot file"
	@find quake -iname "*.py" | xargs xgettext --from-code=UTF-8 --output=quake-python.pot
	@find $(DEV_DATA_DIR) -iname "*.glade" | sed -E "s#$(ROOT_DIR)/##g" | xargs xgettext --from-code=UTF-8 \
	                                                  -L Glade \
	                                                  --output=quake-glade.pot
	@(\
	    find $(DEV_DATA_DIR) -iname "*.desktop" | sed -E "s#$(ROOT_DIR)/##g" | xargs xgettext --from-code=UTF-8 \
		                                                  -L Desktop \
	                                                      --output=quake-desktop.pot \
	) || ( \
	    echo "Skipping .desktop files, is your gettext version < 0.19.1?" && \
	    touch quake-desktop.pot)
	@msgcat --use-first quake-python.pot quake-glade.pot quake-desktop.pot > po/quake.pot
	@rm quake-python.pot quake-glade.pot quake-desktop.pot
	@for f in $$(find po -iname "*.po"); do \
	    echo "updating $$f"; \
	    msgcat --use-first "$$f" po/quake.pot > "$$f.new"; \
	    mv "$$f.new" $$f; \
	done;

pot: update-po

generate-mo:
	@for f in $$(find po -iname "*.po"); do \
	    echo "generating $$f"; \
		l="$${f%%.*}"; \
		msgfmt "$$f" -o "$$l.mo"; \
	done;


generate-desktop:
	@echo "generating desktop files"
	@msgfmt --desktop --template=$(DEV_DATA_DIR)/quake.template.desktop \
		   -d po \
		   -o $(DEV_DATA_DIR)/quake.desktop || ( \
			   	echo "Skipping .desktop files, is your gettext version < 0.19.1?" && \
				cp $(DEV_DATA_DIR)/quake.template.desktop $(DEV_DATA_DIR)/quake.desktop)
	@msgfmt --desktop --template=$(DEV_DATA_DIR)/quake-prefs.template.desktop \
		   -d po \
		   -o $(DEV_DATA_DIR)/quake-prefs.desktop || ( \
			   	echo "Skipping .desktop files, is your gettext version < 0.19.1?" && \
				cp $(DEV_DATA_DIR)/quake-prefs.template.desktop $(DEV_DATA_DIR)/quake-prefs.desktop)

generate-paths:
	@echo "Generating path.py..."
	@cp -f quake/paths.py.in quake/paths.py
	@# Generic
	@sed -i -e 's|{{ LOGIN_DESTOP_PATH }}|""|g' quake/paths.py
	@sed -i -e 's|{{ AUTOSTART_FOLDER }}|""|g' quake/paths.py
	@# Dev environment:
	@sed -i -e 's|{{ LOCALE_DIR }}|get_default_locale_dir()|g' quake/paths.py
	@sed -i -e 's|{{ IMAGE_DIR }}|get_default_image_dir()|g' quake/paths.py
	@sed -i -e 's|{{ QUAKE_THEME_DIR }}|get_default_theme_dir()|g' quake/paths.py
	@sed -i -e 's|{{ GLADE_DIR }}|get_default_glade_dir()|g' quake/paths.py
	@sed -i -e 's|{{ SCHEMA_DIR }}|get_default_schema_dir()|g' quake/paths.py

reno:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run reno new $(SLUG) --edit

reno-lint:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv run reno -q lint

release-note: release-note-github

release-note-github: reno-lint
	@echo
	@echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	@echo "!! Generating release note for GitHub !!"
	@echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	@echo "-------- copy / paste from here --------"
	@# markdown_github to be avoided => gfm output comes in pandoc 2.0.4 release dec 2017
	@pipenv run reno report --earliest-version 3.8.3 --no-show-source --collapse-pre-releases 2>/dev/null | \
		pandoc -f rst -t markdown --markdown-headings=atx --wrap=none --tab-stop 2 | \
		tr '\n' '\r' | \
			sed 's/\r<!-- -->\r//g' | \
			sed 's/\r\-\ \r\r\ /\r-/g' | \
			sed 's/\r\ \ \:\ \ \ /\r    /g' | \
			sed 's/\r\r\ \ \ \ \-\ /\r    - /g' | \
			sed 's/\r\ \ \ \ \-\ /\r  - /g' | \
			sed 's/\r\ \ >\ \-\ /\r  - /g' | \
			sed 's/\\\#/\#/g' | \
		tr '\r' '\n'

# aliases to gracefully handle typos on poor dev's terminal
check: checks
devel: dev
develop: dev
dist: dists
doc: docs
install: install-system
purge: purge-system
pypi: pypi-publish
run: run-local
run-prefs: run-local-prefs
styles: style
uninstall: uninstall-system
upgrade: update
wheel: wheels
