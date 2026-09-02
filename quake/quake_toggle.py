def toggle_quake_by_dbus():
    import dbus  # pylint: disable=import-outside-toplevel

    try:
        bus = dbus.SessionBus()
        remote_object = bus.get_object(
            "org.quake.RemoteControl", "/org/quake/RemoteControl")
        print("Sending 'toggle' message to quake")
        remote_object.show_hide()
    except dbus.DBusException:
        pass
