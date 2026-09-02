# -*- coding: utf-8 -*-

from quake import vte_version
from quake import vte_runtime_version
from quake import quake_version
from quake import gtk_version
from gi.repository import Gdk
import os

import gi

gi.require_version("Gdk", "3.0")


def horizonal_line():
    print("-" * 50)


def populate_display(display):
    screen = display.get_default_screen()
    print(f"Display: {display.get_name()}")
    print()
    # pylint: disable=R1719
    print(f"RGBA visual: {True if screen.get_rgba_visual() else False}")
    print()
    print(f"Composited: {screen.is_composited()}")
    print()

    n_monitors = display.get_n_monitors()
    for i in range(n_monitors):
        monitor = display.get_monitor(i)
        v = " ".join(j for j in (
            monitor.get_manufacturer(), monitor.get_model()) if j)
        print(f"* Monitor: {i} - {v}")

        # Geometry
        rect = monitor.get_geometry()
        scale = monitor.get_scale_factor()
        v = f"{rect.width} x {rect.height}{' % 2' if scale == 2 else ''} at {rect.x}, {rect.y}"
        print(f"    * Geometry:\t\t{v}")

        # Size
        v = f"{monitor.get_width_mm()} x {monitor.get_height_mm()} mm²"
        print(f"    * Size:\t\t{v}")

        # Primary
        print(f"    * Primary:\t\t{monitor.is_primary()}")

        # Refresh rate
        if monitor.get_refresh_rate():
            v = f"{0.001 * monitor.get_refresh_rate()} Hz"
        else:
            v = "unknown"
        print(f"    * Refresh rate:\t{v}")

        # Subpixel layout
        print(
            f"    * Subpixel layout:\t{monitor.get_subpixel_layout().value_nick}")


def get_version():
    display = Gdk.Display.get_default()

    print(f"Quake Version:\t\t{quake_version()}")
    print()
    print(f"Vte Version:\t\t{vte_version()}")
    print()
    print(f"Vte Runtime Version:\t{vte_runtime_version()}")
    print()
    horizonal_line()
    print(f"GTK+ Version:\t\t{gtk_version()}")
    print()
    print(f"GDK Backend:\t\t{str(display).split(' ', maxsplit=1)[0]}")
    print()
    horizonal_line()


def get_desktop_session():
    print(f"Desktop Session: {os.environ.get('DESKTOP_SESSION')}")
    print()
    horizonal_line()


def get_display():
    display = Gdk.Display.get_default()
    populate_display(display)


def print_support():
    print("<details><summary>$ quake --support</summary>")
    print()
    get_version()
    get_desktop_session()
    get_display()
