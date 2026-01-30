#!/usr/bin/env python3
"""
Android Media Bridge for Macropad (Termux-USB Version)
-------------------------------------------------------
USAGE:
   termux-usb -r -e "python host_media_bridge_android.py" /dev/bus/usb/XXX/YYY
"""

import subprocess
import json
import time
import sys
import os

def get_media_info_android():
    """Get currently playing media info using Termux:API"""
    try:
        result = subprocess.run(
            ['termux-notification-list'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            notifications = json.loads(result.stdout)
            for notif in notifications:
                pkg = notif.get('packageName', '')
                title = notif.get('title', '')
                content = notif.get('content', '')
                
                media_apps = ['spotify', 'youtube', 'music', 'player', 'podcast', 'soundcloud', 'deezer', 'tidal']
                if any(app in pkg.lower() for app in media_apps):
                    app_name = pkg.split('.')[-1].capitalize()
                    song = f"{title} - {content}" if content else title
                    if song and song != " - ":
                        return song, app_name
    except Exception:
        pass
    return "No Media Playing", "Android"

def main():
    print("=" * 50)
    print("  Android Media Bridge for Macropad")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\n❌ No file descriptor provided!")
        print("\nUsage:")
        print('  termux-usb -r -e "python host_media_bridge_android.py" /dev/bus/usb/XXX/YYY')
        print("\nTo find your device: termux-usb -l")
        return
    
    fd = int(sys.argv[1])
    print(f"\n📍 Got file descriptor: {fd}")
    
    try:
        # Open the file descriptor for read/write
        # The FD is a raw USB device, not a serial port
        # We need libusb to properly communicate with CDC devices
        
        print("🔧 Attempting USB communication...")
        
        # Try using pyusb with the file descriptor
        try:
            import usb.core
            import usb.util
            
            # Find the Seeed XIAO RP2040
            dev = usb.core.find(idVendor=0x2886)
            
            if dev is None:
                print("❌ Device not found via pyusb")
                demo_mode()
                return
            
            print(f"✅ Found: {dev.manufacturer} - {dev.product}")
            
            # Set configuration
            try:
                dev.set_configuration()
            except usb.core.USBError:
                pass  # Already configured
            
            # Find the CDC data interface endpoints
            cfg = dev.get_active_configuration()
            intf = cfg[(1, 0)]  # Usually CDC data is interface 1
            
            ep_out = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
            ep_in = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
            
            if ep_out is None or ep_in is None:
                print("❌ Could not find USB endpoints")
                demo_mode()
                return
            
            print("✅ Connected! Sending media info...\n")
            
            last_sent = ""
            while True:
                song, app = get_media_info_android()
                full_state = f"{song}|{app}"
                
                if full_state != last_sent:
                    print(f"📡 Sending: {app} - {song}")
                    try:
                        ep_out.write(f"APP:{app}\n".encode('utf-8'))
                        time.sleep(0.05)
                        ep_out.write(f"SONG:{song}\n".encode('utf-8'))
                    except Exception as e:
                        print(f"⚠️ Write error: {e}")
                    last_sent = full_state
                
                time.sleep(0.5)
                
        except ImportError:
            print("\n⚠️ pyusb not installed!")
            print("   Run: pip install pyusb")
            print("   Also: pkg install libusb\n")
            demo_mode()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        demo_mode()

def demo_mode():
    """Show what would be sent to the macropad."""
    print("\n🎭 DEMO MODE - Showing detected media:")
    print("-" * 40)
    
    last_sent = ""
    while True:
        song, app = get_media_info_android()
        full_state = f"{song}|{app}"
        
        if full_state != last_sent:
            print(f"APP:{app}")
            print(f"SONG:{song}")
            print("-" * 40)
            last_sent = full_state
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
