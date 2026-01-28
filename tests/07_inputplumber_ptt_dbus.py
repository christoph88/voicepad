#!/usr/bin/env python3
"""
Test 7: InputPlumber DBus PTT Detection
Listen to back paddle R4 via InputPlumber's DBus interface
"""

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import sys

# Initialize DBus main loop
DBusGMainLoop(set_as_default=True)

print("VoicePad - InputPlumber DBus PTT Test")
print("=" * 50)

try:
    # Connect to system bus
    bus = dbus.SystemBus()
    
    # Get InputPlumber manager
    manager = bus.get_object(
        'org.shadowblip.InputPlumber',
        '/org/shadowblip/InputPlumber'
    )
    
    print("✓ Connected to InputPlumber")
    
    # Get list of composite devices
    introspect = dbus.Interface(manager, 'org.freedesktop.DBus.Introspectable')
    data = introspect.Introspect()
    
    # Look for CompositeDevice0 (should be Steam Deck)
    device_path = '/org/shadowblip/InputPlumber/CompositeDevice0'
    
    # Get the composite device
    composite_device = bus.get_object(
        'org.shadowblip.InputPlumber',
        device_path
    )
    
    # Get device properties
    props_iface = dbus.Interface(composite_device, 'org.freedesktop.DBus.Properties')
    device_name = props_iface.Get('org.shadowblip.Input.CompositeDevice', 'Name')
    print(f"✓ Found device: {device_name}")
    
    # Get the DBus target device path from TargetDevices property
    target_devices = props_iface.Get('org.shadowblip.Input.CompositeDevice', 'TargetDevices')
    dbus_target_path = None
    for target in target_devices:
        if 'dbus' in target:
            dbus_target_path = target
            break
    
    if not dbus_target_path:
        print("✗ No DBus target device found!")
        print(f"Available targets: {target_devices}")
        exit(1)
    
    print(f"\nListening for DBus events on: {dbus_target_path}")
    print("Press back paddle R4 (unmapped) to test PTT")
    print("Press Ctrl+C to exit")
    print("-" * 50)
    
    # Define event handler
    ptt_pressed = False
    
    def on_input_event(event, value):
        global ptt_pressed
        # Filter for R4 back paddle events
        # The event name will depend on how InputPlumber interprets R4
        # Common possibilities: BTN_TR2, KEY_F12, or custom mapping
        
        if 'TR2' in str(event) or 'F12' in str(event) or 'PADDLE' in str(event).upper():
            if value > 0.5 and not ptt_pressed:
                print(f"✓ PTT PRESSED - Event: {event}, Value: {value}")
                ptt_pressed = True
            elif value < 0.5 and ptt_pressed:
                print(f"✓ PTT RELEASED - Event: {event}, Value: {value}")
                ptt_pressed = False
        else:
            # Show all events for debugging
            if value > 0:  # Only show press events to reduce noise
                print(f"  Event: {event}, Value: {value}")
    
    # Subscribe to InputEvent signals
    try:
        dbus_device = bus.get_object('org.shadowblip.InputPlumber', dbus_target_path)
        dbus_device.connect_to_signal(
            'InputEvent',
            on_input_event,
            dbus_interface='org.shadowblip.Input.DBusDevice'
        )
        print("✓ Subscribed to InputEvent signals\n")
    except Exception as e:
        print(f"⚠ Could not subscribe to DBus target: {e}")
        print("This is normal if intercept mode is not enabled yet.")
        print("\nTry enabling intercept mode with:")
        print(f"  inputplumber device 0 intercept set all")
        sys.exit(1)
    
    # Run the main loop
    loop = GLib.MainLoop()
    loop.run()
    
except dbus.exceptions.DBusException as e:
    print(f"\n✗ DBus Error: {e}")
    print("\nMake sure InputPlumber is running:")
    print("  sudo systemctl status inputplumber")
    print("  sudo systemctl start inputplumber")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\nTest stopped by user")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
