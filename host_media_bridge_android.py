#!/usr/bin/env python3
"""
Android Media Bridge for Macropad
---------------------------------
Run this script in Termux to send currently playing media info to the macropad.

REQUIREMENTS:
1. Install Termux from F-Droid (NOT Play Store version)
2. Install Termux:API app from F-Droid
3. In Termux, run:
   pkg install python termux-api
   pip install pyserial

4. Grant notification access to Termux:API in Android Settings

USAGE:
   python host_media_bridge_android.py

NOTE: You may need to find the correct USB device path (usually /dev/bus/usb/... or via OTG)
      For USB serial, you might need root or use a USB serial terminal app instead.
"""

import subprocess
import json
import time
import sys

# --- CONFIGURATION ---
# For USB Serial on Android, you typically need a USB OTG adapter
# and may need to use a serial terminal app or have root access.
# This script provides the logic; serial access may require adaptation.

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("pyserial not installed. Run: pip install pyserial")

def get_media_info_android():
    """
    Get currently playing media info using Termux:API
    Requires: termux-api package and Termux:API app with notification access
    """
    try:
        # Method 1: Use termux-media-player (if available)
        result = subprocess.run(
            ['termux-media-player', 'info'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            info = json.loads(result.stdout)
            if info.get('status') == 'Playing':
                return info.get('track', 'Unknown'), info.get('album', 'Media')
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    
    try:
        # Method 2: Use termux-notification-list to find media notifications
        result = subprocess.run(
            ['termux-notification-list'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            notifications = json.loads(result.stdout)
            for notif in notifications:
                # Look for media-style notifications
                pkg = notif.get('packageName', '')
                title = notif.get('title', '')
                content = notif.get('content', '')
                
                # Common media apps
                if any(app in pkg.lower() for app in ['spotify', 'youtube', 'music', 'player', 'podcast']):
                    app_name = pkg.split('.')[-1].capitalize()
                    song = f"{title} - {content}" if content else title
                    return song, app_name
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    
    return "No Media Playing", "Android"

def find_usb_serial():
    """
    Find USB serial device.
    On Android with Termux, this is tricky without root.
    Common paths: /dev/ttyUSB0, /dev/ttyACM0
    """
    if not SERIAL_AVAILABLE:
        return None
    
    # Try common paths
    common_paths = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
    
    for path in common_paths:
        try:
            ser = serial.Serial(path, 115200, timeout=1)
            ser.close()
            return path
        except (serial.SerialException, OSError):
            continue
    
    # Try using pyserial's port detection
    try:
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.vid == 0x2886:  # Seeed XIAO RP2040
                return port.device
    except Exception:
        pass
    
    return None

def main():
    print("Android Media Bridge for Macropad")
    print("=" * 40)
    
    if not SERIAL_AVAILABLE:
        print("\n[DEMO MODE] pyserial not available.")
        print("Showing media info that WOULD be sent:\n")
        
        while True:
            song, app = get_media_info_android()
            print(f"APP: {app}")
            print(f"SONG: {song}")
            print("-" * 30)
            time.sleep(2)
    
    # Find device
    print("Searching for Macropad...")
    port = find_usb_serial()
    
    if not port:
        print("\nUSB Serial device not found.")
        print("\nNOTE: USB Serial on Android typically requires:")
        print("  1. USB OTG adapter")
        print("  2. Root access OR a USB serial terminal app")
        print("\nAlternative: Use a USB Serial Terminal app like")
        print("  'Serial USB Terminal' and manually send commands.\n")
        
        # Fall back to demo mode
        print("[DEMO MODE] Showing media info:\n")
        while True:
            song, app = get_media_info_android()
            print(f"APP:{app}")
            print(f"SONG:{song}")
            time.sleep(2)
        return
    
    print(f"Connecting to {port}...")
    
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print("Connected! Watching for media changes...\n")
        
        last_sent = ""
        
        while True:
            # Check for PING
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line == "PING":
                        last_sent = ""  # Force resend
                except Exception:
                    pass
            
            song, app = get_media_info_android()
            full_state = f"{song}|{app}"
            
            if full_state != last_sent:
                print(f"Sending: {song} | App: {app}")
                
                ser.write(f"APP:{app}\n".encode('utf-8'))
                time.sleep(0.05)
                ser.write(f"SONG:{song}\n".encode('utf-8'))
                
                last_sent = full_state
            
            time.sleep(0.5)
            
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
