# -*- coding: utf-8; -*-
"""
Copyright (C) 2007-2012 Lincoln de Sousa <lincoln@minaslivre.org>
Copyright (C) 2007 Gabriel Falcão <gabrielteratos@gmail.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301 USA
"""
from gi.repository import Gio
import logging
import subprocess

import gi

from quake import instance

gi.require_version("Gtk", "3.0")

log = logging.getLogger(__name__)

# Each entry is (attribute name, schema id, subpath under the instance's
# dconf root). The schemas in org.quake.gschema.xml are relocatable (they
# carry no path= attribute), so the actual dconf path is built here from
# quake.instance.dconf_path(), which differs between quake instances.
_SCHEMAS = (
    ("quake", "quake", ""),
    ("general", "quake.general", "general/"),
    ("keybindings", "quake.keybindings", "keybindings/"),
    ("keybindingsGlobal", "quake.keybindings.global", "keybindings/global/"),
    ("keybindingsLocal", "quake.keybindings.local", "keybindings/local/"),
    ("styleBackground", "quake.style.background", "style/background/"),
    ("styleFont", "quake.style.font", "style/font/"),
    ("style", "quake.style", "style/"),
    ("hooks", "quake.hooks", "hooks/"),
)


class Settings:
    def __init__(self, schema_source):
        Settings.compat()
        Settings.enhanceSetting()

        dconf_root = instance.dconf_path()

        for attr, schema_id, subpath in _SCHEMAS:
            settings = Gio.Settings.new_full(
                Gio.SettingsSchemaSource.lookup(schema_source, schema_id, False),
                None,
                dconf_root + subpath,
            )
            settings.initEnhancements()
            settings.connect("changed", settings.triggerOnChangedValue)
            setattr(self, attr, settings)

    def enhanceSetting():
        def initEnhancements(self):
            self.listeners = {}

        def onChangedValue(self, key, user_func):
            if key not in self.listeners:
                self.listeners[key] = []
            self.listeners[key].append(user_func)

        def triggerOnChangedValue(self, settings, key, user_data=None):
            if key in self.listeners:
                for func in self.listeners[key]:
                    func(settings, key, user_data)

        gi.repository.Gio.Settings.initEnhancements = initEnhancements
        gi.repository.Gio.Settings.onChangedValue = onChangedValue
        gi.repository.Gio.Settings.triggerOnChangedValue = triggerOnChangedValue

    def compat():
        # This migrates the legacy /apps/quake/ dconf tree (from very old
        # Guake versions) into /org/quake/. There is no such legacy tree for
        # a named instance, so only the default instance needs to check.
        if instance.get_instance() is not None:
            return
        try:
            if len(subprocess.check_output(["dconf", "dump", "/org/quake/"])) == 0:
                prefs = subprocess.check_output(
                    ["dconf", "dump", "/apps/quake/"])
                if len(prefs) > 0:
                    with subprocess.Popen(
                        ["dconf", "load", "/org/quake/"], stdin=subprocess.PIPE
                    ) as p:
                        p.communicate(input=prefs)
        except FileNotFoundError:
            log.exception(
                """First run with newer Quake version detected.
dconf not installed, skipping preferences transfer."""
            )
