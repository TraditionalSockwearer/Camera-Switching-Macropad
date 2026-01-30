#!/usr/bin/env python3
"""
Android Media Bridge for Macropad (Termux-USB Version)
-------------------------------------------------------
Run this script in Termux to send currently playing media info to the macropad.

SETUP:
1. Install Termux from F-Droid (NOT Play Store version)
2. Install Termux:API app from F-Droid
3. In Termux, run:
   pkg install python termux-api
   pip install pyserial

4. Grant notification access to Termux:API in Android Settings > Apps > Termux:API

USAGE (with termux-usb for permission):
   # First, find your device:
   termux-usb -l
   
   # Request permission (replace XXX/YYY with your device path):
   termux-usb -r /dev/bus/usb/XXX/YYY
   
   # Run with USB access:
   termux-usb -e python host_media_bridge_android.py /dev/bus/usb/XXX/YYY

ALTERNATIVE (if you have root):
   su -c "python host_media_bridge_android.py"
"""

import subprocess
import json
import time
import sys
import os

# Check if we're running via termux-usb (file descriptor passed)
USB_FD = None
if len(sys.argv) > 1:
    # When run via termux-usb -e, the USB device path is passed
    USB_DEVICE_PATH = sys.argv[1]
else:
    USB_DEVICE_PATH = None

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("pyserial not installed. Run: pip install pyserial")
    print("Then run again.")

def get_media_info_android():
    """
    Get currently playing media info using Termux:API
    Requires: termux-api package and Termux:API app with notification access
    """
    # Method 1: Try termux-media-player
    try:
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
    
    # Method 2: Use termux-notification-list
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
                
                # Common media apps
                media_apps = ['spotify', 'youtube', 'music', 'player', 'podcast', 'soundcloud', 'deezer', 'tidal']
                if any(app in pkg.lower() for app in media_apps):
                    app_name = pkg.split('.')[-1].capitalize()
                    song = f"{title} - {content}" if content else title
                    if song and song != " - ":
                        return song, app_name
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    
    return "No Media Playing", "Android"

def find_usb_serial():
    """Find USB serial device paths."""
    if not SERIAL_AVAILABLE:
        return None
    
    # If path provided via termux-usb
    if USB_DEVICE_PATH:
        return USB_DEVICE_PATH
    
    # Try common paths
    common_paths = [
        '/dev/ttyUSB0', '/dev/ttyUSB1', 
        '/dev/ttyACM0', '/dev/ttyACM1',
        '/dev/serial/by-id/*'
    ]
    
    for path in common_paths:
        if '*' in path:
            continue
        try:
            # Just check if path exists
            if os.path.exists(path):
                return path
        except Exception:
            continue
    
    return None

def list_usb_devices():
    """List available USB devices using termux-usb."""
    print("\n📱 Listing USB devices...")
    try:
        result = subprocess.run(['termux-usb', '-l'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            devices = json.loads(result.stdout) if result.stdout.strip() else []
            if devices:
                print("Found USB devices:")
                for dev in devices:
                    print(f"  → {dev}")
                return devices
            else:
                print("No USB devices found. Make sure:")
                print("  1. Device is connected via USB OTG")
                print("  2. USB debugging is NOT blocking the connection")
        else:
            print("termux-usb command failed. Install termux-api:")
            print("  pkg install termux-api")
    except FileNotFoundError:
        print("termux-usb not found. Install with: pkg install termux-api")
    except Exception as e:
        print(f"Error: {e}")
    return []

def request_usb_permission(device_path):
    """Request USB permission for a device."""
    print(f"\n🔐 Requesting permission for {device_path}...")
    try:
        result = subprocess.run(
            ['termux-usb', '-r', device_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("✅ Permission granted!")
            return True
        else:
            print("❌ Permission denied or timeout.")
            print("   Try granting permission when the popup appears.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_with_usb_permission(device_path):
    """Run the serial communication with USB permission."""
    print(f"\n🔌 Connecting to {device_path}...")
    
    try:
        import usb.core
        import usb.util
        USB_AVAILABLE = True
    except ImportError:
        USB_AVAILABLE = False
        print("pyusb not installed. Trying direct serial...")
    
    if not SERIAL_AVAILABLE:
        print("pyserial not available!")
        return
    
    try:
        # Try to open serial port
        ser = serial.Serial(device_path, 115200, timeout=1)
        print("✅ Connected! Watching for media changes...\n")
        
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
                print(f"📡 Sending: {song} | App: {app}")
                
                ser.write(f"APP:{app}\n".encode('utf-8'))
                time.sleep(0.05)
                ser.write(f"SONG:{song}\n".encode('utf-8'))
                
                last_sent = full_state
            
            time.sleep(0.5)
            
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
        print("\n💡 Tip: Run with termux-usb for permission:")
        print(f"   termux-usb -r {device_path}")
        print(f"   termux-usb -e python {sys.argv[0]} {device_path}")
    except PermissionError as e:
        print(f"❌ Permission denied: {e}")
        print("\n💡 Solution: Use termux-usb to grant permission:")
        print(f"   termux-usb -r {device_path}")
    except KeyboardInterrupt:
        print("\n👋 Stopping...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def demo_mode():
    """Run in demo mode without serial connection."""
    print("\n🎭 DEMO MODE (no serial connection)")
    print("Showing what would be sent to the macropad:\n")
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

def main():
    print("=" * 50)
    print("  Android Media Bridge for Macropad")
    print("  (Termux-USB Version)")
    print("=" * 50)
    
    if not SERIAL_AVAILABLE:
        print("\n⚠️  pyserial not installed!")
        print("   Run: pip install pyserial\n")
        demo_mode()
        return
    
    # Check if device path was provided
    if USB_DEVICE_PATH:
        print(f"\n📍 Using device: {USB_DEVICE_PATH}")
        run_with_usb_permission(USB_DEVICE_PATH)
        return
    
    # Try to find device automatically
    device = find_usb_serial()
    
    if device:
        print(f"\n📍 Found device: {device}")
        run_with_usb_permission(device)
    else:
        # List devices and guide user
        devices = list_usb_devices()
        
        if devices:
            print("\n📝 To connect, run:")
            print(f"   termux-usb -r {devices[0]}")
            print(f"   termux-usb -e python {sys.argv[0]} {devices[0]}")
        else:
            print("\n📝 No USB device found. Options:")
            print("   1. Connect macropad via USB OTG adapter")
            print("   2. Run 'termux-usb -l' to list devices")
            print("   3. Use demo mode to test media detection\n")
        
        print("\n🎭 Starting demo mode...")
        demo_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
