import sys

from quake import instance


def toggle_quake_by_dbus():
    import dbus  # pylint: disable=import-outside-toplevel

    # Instance is selected the same way as `quake` itself: an explicit
    # argument on the command line, falling back to $QUAKE_INSTANCE, falling
    # back to the default (unnamed) instance.
    name = sys.argv[1] if len(sys.argv) > 1 else instance.resolve_from_environment()
    instance.set_instance(name)

    try:
        bus = dbus.SessionBus()
        remote_object = bus.get_object(
            instance.dbus_name(), instance.dbus_path())
        print(f"Sending 'toggle' message to {instance.display_name()}")
        remote_object.show_hide()
    except dbus.DBusException:
        pass
