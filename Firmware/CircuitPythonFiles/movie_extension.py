import displayio
import terminalio
import time
import board
import neopixel
import usb_cdc
import gc
import asyncio
from digitalio import DigitalInOut, Direction
from adafruit_display_text import bitmap_label
from kmk.extensions import Extension
from movie_data import FRAMES, ANIM_PREV, ANIM_NEXT, ANIM_PAUSE, ANIM_PLAY, ANIM_MUTE, ANIM_UNMUTE


class MovieExtension(Extension):
    def __init__(self, display):
        self.display = display


        self.pixel_power = DigitalInOut(board.NEOPIXEL_POWER)
        self.pixel_power.direction = Direction.OUTPUT
        self.pixel_power.value = True

        self.pixel_onboard = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=False)

        self.pixel_strip = neopixel.NeoPixel(board.D6, 4, brightness=0.3, auto_write=False)

        # LED State
        self.current_color = [0, 0, 0]
        self.target_color = [0, 0, 0]
        self.fade_speed = 2  # Speed of fade (Higher = Faster)

        self.is_playing = False
        self.last_tick = 0
        self.frame_index = 0
        self.target_text = "READY"
        self.is_paused = False # Assume playing initially
        self.is_muted = False # Assume unmuted initially

        self.main_group = displayio.Group()
        self.anim_group = displayio.Group()
        self.text_group = displayio.Group()

        # Load Animations
        self.bitmaps = {}
        self.bitmaps['DEFAULT'] = self._create_bitmap(FRAMES)
        self.bitmaps['PREVIOUS'] = self._create_bitmap(ANIM_PREV)
        self.bitmaps['NEXT'] = self._create_bitmap(ANIM_NEXT)
        self.bitmaps['PAUSE'] = self._create_bitmap(ANIM_PAUSE)
        self.bitmaps['PLAY'] = self._create_bitmap(ANIM_PLAY)
        self.bitmaps['MUTE'] = self._create_bitmap(ANIM_MUTE)
        self.bitmaps['UNMUTE'] = self._create_bitmap(ANIM_UNMUTE)
        
        self.current_anim_len = len(FRAMES)

        self.palette = displayio.Palette(2)
        self.palette[0] = 0x000000
        self.palette[1] = 0xFFFFFF
        
        # Initial TileGrid (Default)
        self.tile_grid = displayio.TileGrid(
            self.bitmaps['DEFAULT'], pixel_shader=self.palette,
            width=1, height=1, tile_width=32, tile_height=32,
            x=48, y=0
        )
        self.anim_group.append(self.tile_grid)
        self.text_area = bitmap_label.Label(
            terminalio.FONT, text="READY", color=0xFFFFFF, scale=2, x=34, y=10
        )
        self.text_group.append(self.text_area)

        # Scrolling Group
        self.scroll_group = displayio.Group()
        
        # App Label (Static, Top)
        self.app_label = bitmap_label.Label(
            terminalio.FONT, text="System", color=0xFFFFFF, scale=1, x=2, y=6
        )
        self.scroll_group.append(self.app_label)
        
        # Scroll Label (Scrolling, Bottom)
        self.scroll_label = bitmap_label.Label(
            terminalio.FONT, text="Wait for PC...", color=0xFFFFFF, scale=2, x=128, y=24
        )
        self.scroll_group.append(self.scroll_label)
        
        self.scroll_text_val = "Wait for PC..."
        self.scroll_x = 0
        self.scroll_direction = -1
        self.scroll_pause = False
        self.pause_start = 0
        self.last_scroll_time = 0
        self.last_ping_time = 0
        self.last_gc_time = 0
        self.current_mode = None # Track current mode: 'MENU', 'MEDIA', 'OBS'


        # Menu Group
        self.menu_group = displayio.Group()
        menu_label = bitmap_label.Label(
            terminalio.FONT, text="OBS  MEDIA", color=0xFFFFFF, scale=2, x=8, y=16
        )
        self.menu_group.append(menu_label)



        for args in [(128, 1, 0, 0), (128, 1, 0, 31), (1, 32, 0, 0), (1, 32, 127, 0)]:
            w, h, x, y = args
            self.text_group.append(displayio.TileGrid(displayio.Bitmap(w, h, 1), pixel_shader=self.palette, x=x, y=y))

        self.main_group.append(self.text_group)
        self.display.root_group = self.main_group

    def _create_bitmap(self, frames):
        total_frames = len(frames)
        bmp = displayio.Bitmap(32, 32 * total_frames, 2)
        for f_idx, frame_bytes in enumerate(frames):
            if len(frame_bytes) < 128: frame_bytes += b'\x00' * (128 - len(frame_bytes))
            y_offset = f_idx * 32
            for y in range(32):
                for byte_col in range(4):
                    byte_val = frame_bytes[y * 4 + byte_col]
                    for bit in range(8):
                        if byte_val & (0x80 >> bit):
                            bmp[byte_col * 8 + bit, y_offset + y] = 1
        return bmp

    def play_animation(self, text_after, color_rgb):
        """Triggers animation and sets new LED target color."""
        # LED Target
        self._fade_leds_to(color_rgb)

        if self.is_playing: return

        print(f"Animation: {text_after} | Color: {color_rgb}")
        self.target_text = text_after
        self.frame_index = 0
        self.is_playing = True
        self.last_tick = time.monotonic()
        
        # Select Animation
        anim_key = 'DEFAULT'
        if text_after == "PREVIOUS":
            anim_key = 'PREVIOUS'
            self.current_anim_len = len(ANIM_PREV)
        elif text_after == "NEXT":
            anim_key = 'NEXT'
            self.current_anim_len = len(ANIM_NEXT)
        elif text_after == "PLAY/PAUSE":
            # Toggle State
            self.is_paused = not self.is_paused
            if self.is_paused:
                anim_key = 'PAUSE' # Going to Pause state
                self.current_anim_len = len(ANIM_PAUSE)
            else:
                anim_key = 'PLAY' # Going to Play state
                self.current_anim_len = len(ANIM_PLAY)
        elif text_after == "MUTE":
            # Toggle Mute State
            self.is_muted = not self.is_muted
            if self.is_muted:
                anim_key = 'MUTE'
                self.current_anim_len = len(ANIM_MUTE)
            else:
                anim_key = 'UNMUTE'
                self.current_anim_len = len(ANIM_UNMUTE)
        else:
            self.current_anim_len = len(FRAMES)
            
        # Recreate TileGrid to handle different bitmap sizes
        if self.tile_grid:
            self.anim_group.remove(self.tile_grid)
        
        self.tile_grid = displayio.TileGrid(
            self.bitmaps[anim_key], pixel_shader=self.palette,
            width=1, height=1, tile_width=32, tile_height=32,
            x=48, y=0
        )
        self.anim_group.append(self.tile_grid)


        while len(self.main_group) > 0: self.main_group.pop()
        self.main_group.append(self.anim_group)

    def show_menu(self):
        """Switches display to Menu Mode"""
        self.current_mode = 'MENU'
        self.is_playing = False
        while len(self.main_group) > 0: self.main_group.pop()
        self.main_group.append(self.menu_group)
        self._fade_leds_to((0, 0, 0))

    def show_scrolling_text(self):
        """Switches display to Scrolling Text Mode (Media)"""
        self.current_mode = 'MEDIA'
        self.is_playing = False
        while len(self.main_group) > 0: self.main_group.pop()
        self.main_group.append(self.scroll_group)
        self._fade_leds_to((0, 0, 255))

    def show_status(self, text, color_rgb):
        """Shows static status text without animation"""
        self.current_mode = 'OBS'
        self.is_playing = False
        self.target_text = text
        self.text_area.text = text
        # Center text roughly
        new_x = max(2, (128 - (len(text) * 12)) // 2)
        self.text_area.x = int(new_x)
        
        while len(self.main_group) > 0: self.main_group.pop()
        self.main_group.append(self.text_group)
        self._fade_leds_to(color_rgb)

    def update_scrolling_text(self):
        # 1. Read Serial
        if usb_cdc.data.in_waiting > 0:
            try:
                data = usb_cdc.data.read(usb_cdc.data.in_waiting)
                text_chunk = data.decode("utf-8")

                lines = text_chunk.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    
                    if line.startswith("SONG:"):
                        new_song = line[5:]
                        if new_song != self.scroll_text_val:
                            self.scroll_text_val = new_song
                            self.scroll_label.text = new_song
                            self.scroll_x = 0 
                            self.scroll_direction = -1 
                            self.scroll_pause = True 
                            self.pause_start = time.monotonic()
                            gc.collect() 
                            
                    elif line.startswith("APP:"):
                        new_app = line[4:].strip()
                        new_app_x = max(0, (128 - (len(new_app) * 6)) // 2)
                        self.app_label.text = new_app
                        self.app_label.x = int(new_app_x)
                    
            except Exception:
                pass

        # 2. Scroll Logic (only if active)
        if self.scroll_group in self.main_group:
             now = time.monotonic()
             text_width = len(self.scroll_text_val) * 12
             display_width = 128
             
             if text_width <= display_width:
                 self.scroll_label.x = 0
             elif self.scroll_pause:
                 if now - self.pause_start > 2.0: # 2 second pause
                     self.scroll_pause = False
             elif now - self.last_scroll_time > 0.01: # Fast speed
                 self.last_scroll_time = now
                 self.scroll_x += self.scroll_direction
                 
                 # Bounce Logic
                 min_x = display_width - text_width
                 
                 if self.scroll_x <= min_x:
                     self.scroll_x = min_x
                     self.scroll_direction = 1 # Go Right
                     self.scroll_pause = True
                     self.pause_start = now
                 elif self.scroll_x >= 0:
                     self.scroll_x = 0
                     self.scroll_direction = -1 # Go Left
                     self.scroll_pause = True
                     self.pause_start = now
                     
                 self.scroll_label.x = int(self.scroll_x)

    async def loop(self):
        while True:
            # Rate-limited GC
            if time.monotonic() - self.last_gc_time > 5.0:
                self.last_gc_time = time.monotonic()
                gc.collect()

            self.update_scrolling_text()
            
            # Ping Logic
            now = time.monotonic()
            if now - self.last_ping_time > 60.0:
                self.last_ping_time = now
                if usb_cdc.data and usb_cdc.data.connected:
                    try:
                        usb_cdc.data.write(b"PING\n")
                    except Exception:
                        pass

            if self.is_playing:
                now = time.monotonic()
                if now - self.last_tick > 0.042:
                    self.last_tick = now
                    self.frame_index += 1

                    if self.frame_index >= self.current_anim_len:
                        self.is_playing = False
                        
                        if self.current_mode == 'MEDIA':
                            while len(self.main_group) > 0: self.main_group.pop()
                            self.main_group.append(self.scroll_group)
                        elif self.current_mode == 'MENU':
                            while len(self.main_group) > 0: self.main_group.pop()
                            self.main_group.append(self.menu_group)
                        else:
                            if self.text_area:
                                self.text_area.text = self.target_text
                                new_x = max(2, (128 - (len(self.target_text) * 12)) // 2)
                                self.text_area.x = int(new_x)

                            while len(self.main_group) > 0: self.main_group.pop()
                            self.main_group.append(self.text_group)
                    else:
                        if self.tile_grid: self.tile_grid[0] = self.frame_index
            
            await asyncio.sleep(0.01)

    def before_matrix_scan(self, sandbox):
        pass

    def _fade_leds_to(self, color):
        self.target_color = list(color)
        self.pixel_onboard.fill(tuple(self.target_color))
        self.pixel_onboard.write()
        self.pixel_strip.fill(tuple(self.target_color))
        self.pixel_strip.write()

    # Boilerplate
    def on_runtime_enable(self, sandbox): pass
    def on_runtime_disable(self, sandbox): pass
    def during_bootup(self, keyboard): return
    def after_matrix_scan(self, sandbox): pass
    def before_hid_send(self, sandbox): pass
    def after_hid_send(self, sandbox): pass
    def on_powersave_enable(self, sandbox): pass
    def on_powersave_disable(self, sandbox): pass
