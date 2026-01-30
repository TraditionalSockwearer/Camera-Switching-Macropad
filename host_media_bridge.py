import asyncio
import serial
import serial.tools.list_ports
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

# --- CONFIGURATION ---
TARGET_VID = 0x2886  # Seeeduino Xiao RP2040 VID
# You might need to change PID or check comport if auto-detection fails.

async def get_media_info():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    
    if current_session:
        try:
            info = await current_session.try_get_media_properties_async()
            song = f"{info.title} - {info.artist}"
            
            # Get App Name
            app_id = current_session.source_app_user_model_id
            app_name = app_id.split("!")[-1] if "!" in app_id else app_id
            if app_name.lower().endswith(".exe"):
                app_name = app_name[:-4]
            app_name = app_name.capitalize()
            
            return song, app_name
        except Exception:
            pass
    return "No Media Playing", "Windows"

def find_device_port():
    ports = serial.tools.list_ports.comports()
    matching_ports = []
    for port in ports:
        if port.vid == TARGET_VID:
            matching_ports.append(port.device)
    
    if matching_ports:
        # If we have multiple ports (Console + Data), Data is usually the second one.
        if len(matching_ports) > 1:
            print(f"Found multiple ports: {matching_ports}. Selecting the second one (Data).")
            return matching_ports[1]
        return matching_ports[0]
            
    return None

async def main():
    while True:
        print("Searching for Macropad...")
        port = find_device_port()
        if not port:
            print(f"Device with VID {hex(TARGET_VID)} not found. Waiting...")
            await asyncio.sleep(3)
            continue
    
        print(f"Connecting to {port}...")
        
        try:
            # Open Serial Connection
            # Note: If this connects to REPL by accident, it might echo commands. 
            # But we enabled data=True in boot.py, so there should be a distinct COM port for data.
            # If your device shows 2 COM ports, trying the second one is a good guess.
            ser = serial.Serial(port, 115200, timeout=1)
            print("Connected! Watching for media changes...")
            
            last_sent = ""
            
            while True:
                # Check for incoming data (e.g. PING)
                if ser.in_waiting > 0:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        if line == "PING":
                            # Resend current info
                            # print("Received PING") # Optional debug
                            last_sent = "" # Force resend
                    except Exception:
                        pass
    
                song_info, app_name = await get_media_info()
                
                full_state = f"{song_info}|{app_name}"
                
                if full_state != last_sent:
                    print(f"Sending: {song_info} | App: {app_name}")
                    
                    # Send App Name first
                    msg_app = f"APP:{app_name}\n".encode("utf-8")
                    ser.write(msg_app)
                    await asyncio.sleep(0.05) 
                    
                    # Send Song
                    msg_song = f"SONG:{song_info}\n".encode("utf-8")
                    ser.write(msg_song)
                    
                    last_sent = full_state
                    
                await asyncio.sleep(0.1)
                
        except (serial.SerialException, OSError) as e:
            print(f"Connection lost: {e}")
            print("Reconnecting in 3 seconds...")
            await asyncio.sleep(3)
        except KeyboardInterrupt:
            print("\nStopping...")
            break
        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
