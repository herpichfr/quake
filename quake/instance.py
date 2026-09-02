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
"""Instance identity for quake.

quake can run several independent drop-down terminals side by side. Each one
is an "instance", identified by a short name given with --instance/-I on the
command line or through the QUAKE_INSTANCE environment variable. The instance
with no name is the default one, and it deliberately keeps every path and
identifier quake used before instances existed, so an existing installation
keeps its configuration, its session file and its D-Bus name untouched.

This module is the single source of truth for everything that must differ
between instances: the D-Bus well-known name, the dconf subtree holding the
GSettings values, the config directory holding the tab session, the program
name (hence WM_CLASS), the user visible name and the autostart file name.

The instance is resolved once, early in quake.main, and must be set before
quake.dbusiface or quake.quake_app are imported: both read values from here at
import time.
"""

import builtins
import logging
import os
import re
import sys

from pathlib import Path

log = logging.getLogger(__name__)

# An instance name ends up inside a D-Bus well-known name, a dconf path, a
# file name and a shell command line, so keep it to characters that are safe
# in all four.
VALID_NAME = re.compile(r"^[A-Za-z0-9_-]{1,32}$")

ENV_VAR = "QUAKE_INSTANCE"

# The default (unnamed) instance. Every value below falls back to exactly what
# quake used before multi-instance support was added.
DEFAULT_DBUS_NAME = "org.quake.RemoteControl"
DEFAULT_DBUS_PATH = "/org/quake/RemoteControl"
DEFAULT_DCONF_PATH = "/org/quake/"
DEFAULT_PRGNAME = "quake"
DEFAULT_DISPLAY_NAME = "Quake Terminal"

# Named instances live in a sibling dconf subtree rather than underneath
# /org/quake/. That keeps "dconf dump /org/quake/" (used by --save-preferences
# and --restore-preferences) scoped to the default instance alone: nesting
# would make a default-instance --restore-preferences silently overwrite the
# settings of every named instance too.
INSTANCES_DCONF_ROOT = "/org/quake-instances/"

_instance = None


def set_instance(name):
    """Select the instance this process belongs to.

    `name` may be None or empty, which selects the default (unnamed) instance.
    An invalid name is a hard error: continuing would build a malformed D-Bus
    name or dconf path and fail later with a far more confusing message.
    """
    global _instance  # pylint: disable=global-statement

    if not name:
        _instance = None
        return None

    if not VALID_NAME.match(name):
        sys.stderr.write(
            f"quake: invalid instance name {name!r}\n"
            "Instance names may contain only letters, digits, '-' and '_', "
            "and must be 1 to 32 characters long.\n"
        )
        sys.exit(1)

    _instance = name
    log.info("Running as quake instance: %s", name)
    return _instance


def get_instance():
    """Return the current instance name, or None for the default instance."""
    return _instance


def resolve_from_environment():
    """Return the instance name configured in the environment, or None."""
    return os.environ.get(ENV_VAR) or None


def dbus_name():
    """The D-Bus well-known name this instance owns."""
    if _instance is None:
        return DEFAULT_DBUS_NAME
    # '-' is not legal in a D-Bus name element, but '_' is.
    return f"{DEFAULT_DBUS_NAME}.{_instance.replace('-', '_')}"


def dbus_path():
    """The D-Bus object path. Shared by every instance, since the object is
    already namespaced by the well-known name returned by dbus_name()."""
    return DEFAULT_DBUS_PATH


def dconf_path():
    """The dconf subtree holding this instance's GSettings values.

    Always starts and ends with '/', so it can be concatenated directly with
    a schema subpath such as "keybindings/global/".
    """
    if _instance is None:
        return DEFAULT_DCONF_PATH
    return f"{INSTANCES_DCONF_ROOT}{_instance}/"


def config_dir():
    """Directory holding this instance's tab session file."""
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    base = Path(xdg_config_home, "quake").expanduser()
    if _instance is None:
        return base
    return base / "instances" / _instance


def widget_name():
    """GTK widget name for the main window, used only for CSS selector
    matching in a user's own gtk.css. Kept as the literal 'quake-terminal'
    for the default instance (exactly what quake used before instances
    existed, so an existing custom theme keeps matching), with the instance
    name appended for a named instance."""
    if _instance is None:
        return "quake-terminal"
    return f"quake-terminal-{_instance}"


def prgname():
    """GLib program name, which is also the X11 WM_CLASS. Distinct per
    instance so the window manager can tell the windows apart."""
    if _instance is None:
        return DEFAULT_PRGNAME
    return f"{DEFAULT_PRGNAME}-{_instance}"


def display_name():
    """User visible name, used in window titles, the tray icon tooltip and
    notifications, so it is clear which instance is being talked about.

    The base name is translated the same way every existing _("Quake
    Terminal") call site already did; the instance name itself is a
    user-chosen identifier and is left as-is. Translation is looked up
    dynamically since some entry points (e.g. quake-toggle) never install
    the gettext "_" builtin that quake.main sets up.
    """
    translate = builtins.__dict__.get("_", lambda s: s)
    base = translate(DEFAULT_DISPLAY_NAME)
    if _instance is None:
        return base
    return f"{base} ({_instance})"


def autostart_filename():
    """Name of the .desktop file this instance writes into
    ~/.config/autostart. Distinct per instance so two instances do not fight
    over a single file."""
    if _instance is None:
        return "quake.desktop"
    return f"quake-{_instance}.desktop"


def cli_args():
    """The command line arguments needed to address this instance, for
    building Exec= lines and similar."""
    if _instance is None:
        return []
    return ["--instance", _instance]


def export_to_environment():
    """Publish the instance in the environment, so that a quake invoked from
    inside one of this instance's terminals (e.g. 'quake -t') addresses this
    instance rather than the default one."""
    if _instance is None:
        os.environ.pop(ENV_VAR, None)
    else:
        os.environ[ENV_VAR] = _instance
