# -*- coding: utf-8; -*-
"""
Copyright (C) 2007-2013 Quake authors

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

# pylint: disable=import-outside-toplevel

# Every quake submodule that touches gi.repository is expected to call
# gi.require_version() for the namespaces it needs before importing them.
# But PyGObject only lets a namespace's version be picked once per process:
# whichever module is imported *first* effectively decides the version for
# everyone, and an unversioned `from gi.repository import Gtk` auto-selects
# the newest installed version (Gtk 4 here) rather than erroring. Since
# quake is a GTK3 application (its .glade files and Vte/Keybinder/Wnck
# bindings are all GTK3-only), pin every namespace quake uses here, in
# quake/__init__.py, which always runs before any submodule -- this makes
# per-file require_version() calls elsewhere safe regardless of which
# submodule happens to be imported first.
try:
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    gi.require_version("Vte", "2.91")
    gi.require_version("Keybinder", "3.0")
    gi.require_version("Wnck", "3.0")
    gi.require_version("Notify", "0.7")
except (ImportError, ValueError):
    # gi (PyGObject) and its typelibs are not required just to import the
    # "quake" package -- e.g. quake_version() is used during documentation
    # builds where no GTK stack is installed at all.
    pass


def quake_version():
    from ._version import version

    return version


def vte_version():
    import gi

    gi.require_version("Vte", "2.91")

    from gi.repository import Vte

    s = f"{Vte.MAJOR_VERSION}.{Vte.MINOR_VERSION}.{Vte.MICRO_VERSION}"
    return s


def vte_runtime_version():
    import gi

    gi.require_version("Vte", "2.91")

    from gi.repository import Vte

    return f"{Vte.get_major_version()}.{Vte.get_minor_version()}.{Vte.get_micro_version()}"


def gtk_version():
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    return f"{Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}"
