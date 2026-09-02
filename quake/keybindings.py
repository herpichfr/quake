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
from quake.split_utils import SplitMover
from quake.split_utils import FocusMover
from quake.common import pixmapfile
from quake import notifier
from gi.repository import Gtk
from gi.repository import Gdk
import logging

from collections import defaultdict

import gi

gi.require_version("Gtk", "3.0")


log = logging.getLogger(__name__)


class Keybindings:

    """Handles changes in keyboard shortcuts."""

    def __init__(self, quake):
        """Constructor of Keyboard, only receives the quake instance
        to be used in internal methods.
        """
        self.quake = quake
        self.accel_group = None  # see reload_accelerators
        self._lookup = None
        self._masks = None
        self.keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())

        # Setup global keys
        self.globalhotkeys = {}
        globalkeys = ["show-hide", "show-focus"]
        for key in globalkeys:
            quake.settings.keybindingsGlobal.onChangedValue(
                key, self.reload_global)
            quake.settings.keybindingsGlobal.triggerOnChangedValue(
                quake.settings.keybindingsGlobal, key, None
            )

        def x(*args):
            prompt_cfg = self.quake.settings.general.get_int(
                "prompt-on-close-tab")
            self.quake.get_notebook().delete_page_current(prompt=prompt_cfg)

        # Setup local keys
        self.keys = [
            ("toggle-fullscreen", self.quake.accel_toggle_fullscreen),
            ("new-tab", self.quake.accel_add),
            ("new-tab-home", self.quake.accel_add_home),
            ("new-tab-cwd", self.quake.accel_add_cwd),
            ("close-tab", x),
            ("rename-current-tab", self.quake.accel_rename_current_tab),
            ("previous-tab", self.quake.accel_prev),
            ("previous-tab-alt", self.quake.accel_prev),
            ("next-tab", self.quake.accel_next),
            ("next-tab-alt", self.quake.accel_next),
            ("clipboard-copy", self.quake.accel_copy_clipboard),
            ("clipboard-paste", self.quake.accel_paste_clipboard),
            ("select-all", self.quake.accel_select_all),
            ("quit", self.quake.accel_quit),
            ("zoom-in", self.quake.accel_zoom_in),
            ("zoom-in-alt", self.quake.accel_zoom_in),
            ("zoom-out", self.quake.accel_zoom_out),
            ("increase-height", self.quake.accel_increase_height),
            ("decrease-height", self.quake.accel_decrease_height),
            ("increase-transparency", self.quake.accel_increase_transparency),
            ("decrease-transparency", self.quake.accel_decrease_transparency),
            ("toggle-transparency", self.quake.accel_toggle_transparency),
            ("search-on-web", self.quake.search_on_web),
            ("open-link-under-terminal-cursor",
             self.quake.open_link_under_terminal_cursor),
            ("move-tab-left", self.quake.accel_move_tab_left),
            ("move-tab-right", self.quake.accel_move_tab_right),
            ("switch-tab1", self.quake.gen_accel_switch_tabN(0)),
            ("switch-tab2", self.quake.gen_accel_switch_tabN(1)),
            ("switch-tab3", self.quake.gen_accel_switch_tabN(2)),
            ("switch-tab4", self.quake.gen_accel_switch_tabN(3)),
            ("switch-tab5", self.quake.gen_accel_switch_tabN(4)),
            ("switch-tab6", self.quake.gen_accel_switch_tabN(5)),
            ("switch-tab7", self.quake.gen_accel_switch_tabN(6)),
            ("switch-tab8", self.quake.gen_accel_switch_tabN(7)),
            ("switch-tab9", self.quake.gen_accel_switch_tabN(8)),
            ("switch-tab10", self.quake.gen_accel_switch_tabN(9)),
            ("switch-tab-last", self.quake.accel_switch_tab_last),
            ("reset-terminal", self.quake.accel_reset_terminal),
            (
                "split-tab-vertical",
                lambda *args: self.quake.get_notebook()
                .get_current_terminal()
                .get_parent()
                .split_v()
                or True,
            ),
            (
                "split-tab-horizontal",
                lambda *args: self.quake.get_notebook()
                .get_current_terminal()
                .get_parent()
                .split_h()
                or True,
            ),
            (
                "close-terminal",
                lambda *args: self.quake.get_notebook().get_current_terminal().kill() or True,
            ),
            (
                "focus-terminal-up",
                (
                    lambda *args: FocusMover(self.quake.window).move_up(
                        self.quake.get_notebook().get_current_terminal()
                    )
                    or True
                ),
            ),
            (
                "focus-terminal-down",
                (
                    lambda *args: FocusMover(self.quake.window).move_down(
                        self.quake.get_notebook().get_current_terminal()
                    )
                    or True
                ),
            ),
            (
                "focus-terminal-right",
                (
                    lambda *args: FocusMover(self.quake.window).move_right(
                        self.quake.get_notebook().get_current_terminal()
                    )
                    or True
                ),
            ),
            (
                "focus-terminal-left",
                (
                    lambda *args: FocusMover(self.quake.window).move_left(
                        self.quake.get_notebook().get_current_terminal()
                    )
                    or True
                ),
            ),
            (
                "move-terminal-split-up",
                (
                    lambda *args: SplitMover.move_up(  # keep make style from concat this lines
                        self.quake.get_notebook().get_current_terminal()
                    )
                    or True
                ),
            ),
            (
                "move-terminal-split-down",
                (
                    lambda *args: SplitMover.move_down(  # keep make style from concat this lines
                        self.quake.get_notebook().get_current_terminal()
                    )
                    or True
                ),
            ),
            (
                "move-terminal-split-left",
                (
                    lambda *args: SplitMover.move_left(  # keep make style from concat this lines
                        self.quake.get_notebook().get_current_terminal()
                    )
                    or True
                ),
            ),
            (
                "move-terminal-split-right",
                (
                    lambda *args: SplitMover.move_right(  # keep make style from concat this lines
                        self.quake.get_notebook().get_current_terminal()
                    )
                    or True
                ),
            ),
            ("search-terminal", self.quake.accel_search_terminal),
            ("toggle-hide-on-lose-focus", self.quake.accel_toggle_hide_on_lose_focus),
        ]
        for key, _ in self.keys:
            quake.settings.keybindingsLocal.onChangedValue(
                key, self.reload_accelerators)
        self.reload_accelerators()

    def reload_global(self, settings, key, user_data):
        value = settings.get_string(key)
        if value == "disabled":
            return

        try:
            self.quake.hotkeys.unbind(self.globalhotkeys[key])
        except BaseException:
            pass

        self.globalhotkeys[key] = value
        if key == "show-hide":
            log.debug("reload_global: %r", value)
            if not self.quake.hotkeys.bind(value, self.quake.show_hide):
                keyval, mask = Gtk.accelerator_parse(value)
                label = Gtk.accelerator_get_label(keyval, mask)
                filename = pixmapfile("quake-notification.png")
                notifier.showMessage(
                    _("Quake Terminal"),
                    _(
                        "A problem happened when binding <b>%s</b> key.\n"
                        "Please use Quake Preferences dialog to choose another "
                        "key"
                    )
                    % label,
                    filename,
                )
        elif key == "show-focus" and not self.quake.hotkeys.bind(value, self.quake.show_focus):
            log.warning("can't bind show-focus key")

    def activate(self, window, event):
        """If keystroke matches a key binding, activate keybinding. Otherwise, allow
        keystroke to pass through."""
        key = event.keyval
        mod = event.state

        # Set keyval to the first available English keyboard value if character is non-latin
        # and a english keyval is found
        if event.keyval > 126:
            for i in self.keymap.get_entries_for_keycode(event.hardware_keycode)[2]:
                if 0 < i <= 126:
                    key = i
                    break

        if mod & Gdk.ModifierType.SHIFT_MASK:
            if key == Gdk.KEY_ISO_Left_Tab:
                key = Gdk.KEY_Tab
            else:
                key = Gdk.keyval_to_lower(key)
        else:
            keys = Gdk.keyval_convert_case(key)
            if key != keys[1]:
                key = keys[0]
                mod &= ~Gdk.ModifierType.SHIFT_MASK

        mask = mod & self._masks

        func = self._lookup[mask].get(key, None)
        if func:
            func()
            return True

        return False

    def reload_accelerators(self, *args):
        """Reassign an accel_group to quake main window and quake
        context menu and calls the load_accelerators method.
        """
        self._lookup = defaultdict(dict)
        self._masks = 0

        self.load_accelerators()
        self.quake.accel_group = self

    def load_accelerators(self):
        """Reads all gconf paths under /org/quake/keybindings/local
        and adds to the _lookup.
        """

        for binding, action in self.keys:
            key, mask = Gtk.accelerator_parse(
                self.quake.settings.keybindingsLocal.get_string(binding)
            )
            if key > 0:
                self._lookup[mask][key] = action
                self._masks |= mask
