import displayio
import terminalio
import time
import board
import neopixel
from digitalio import DigitalInOut, Direction
from adafruit_display_text import label
from kmk.extensions import Extension
from movie_data import FRAMES

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

        self.main_group = displayio.Group()
        self.anim_group = displayio.Group()
        self.text_group = displayio.Group()

        # Load Animation
        total_frames = len(FRAMES)
        self.bitmap = displayio.Bitmap(32, 32 * total_frames, 2)

        for f_idx, frame_bytes in enumerate(FRAMES):
            if len(frame_bytes) < 128: frame_bytes += b'\x00' * (128 - len(frame_bytes))
            y_offset = f_idx * 32
            for y in range(32):
                for byte_col in range(4):
                    byte_val = frame_bytes[y * 4 + byte_col]
                    for bit in range(8):
                        if byte_val & (0x80 >> bit):
                            self.bitmap[byte_col * 8 + bit, y_offset + y] = 1

        self.palette = displayio.Palette(2)
        self.palette[0] = 0x000000
        self.palette[1] = 0xFFFFFF
        self.tile_grid = displayio.TileGrid(
            self.bitmap, pixel_shader=self.palette,
            width=1, height=1, tile_width=32, tile_height=32,
            x=48, y=0
        )
        self.anim_group.append(self.tile_grid)
        self.text_area = label.Label(
            terminalio.FONT, text="READY", color=0xFFFFFF, scale=2, x=34, y=10
        )
        self.text_group.append(self.text_area)

        # Menu Group
        self.menu_group = displayio.Group()
        menu_label = label.Label(
            terminalio.FONT, text="OBS  MEDIA", color=0xFFFFFF, scale=2, x=8, y=16
        )
        self.menu_group.append(menu_label)



        for args in [(128, 1, 0, 0), (128, 1, 0, 31), (1, 32, 0, 0), (1, 32, 127, 0)]:
            w, h, x, y = args
            self.text_group.append(displayio.TileGrid(displayio.Bitmap(w, h, 1), pixel_shader=self.palette, x=x, y=y))

        self.main_group.append(self.text_group)
        self.display.root_group = self.main_group

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


        while len(self.main_group) > 0: self.main_group.pop()
        self.main_group.append(self.anim_group)

    def show_menu(self):
        """Switches display to Menu Mode"""
        self.is_playing = False
        while len(self.main_group) > 0: self.main_group.pop()
        self.main_group.append(self.menu_group)
        self._fade_leds_to((0, 0, 0))

    def show_status(self, text, color_rgb):
        """Shows static status text without animation"""
        self.is_playing = False
        self.target_text = text
        self.text_area.text = text
        # Center text roughly
        new_x = max(2, (128 - (len(text) * 12)) // 2)
        self.text_area.x = int(new_x)
        
        while len(self.main_group) > 0: self.main_group.pop()
        self.main_group.append(self.text_group)
        self._fade_leds_to(color_rgb)

    def before_matrix_scan(self, sandbox):
        # Fade Logic

        self._fade_leds()
        if self.is_playing:
            now = time.monotonic()
            if now - self.last_tick > 0.042:
                self.last_tick = now
                self.frame_index += 1

                if self.frame_index >= len(FRAMES):
                    self.is_playing = False
                    if self.text_area:
                        self.text_area.text = self.target_text
                        new_x = max(2, (128 - (len(self.target_text) * 12)) // 2)
                        self.text_area.x = int(new_x)

                    while len(self.main_group) > 0: self.main_group.pop()
                    self.main_group.append(self.text_group)
                else:
                    if self.tile_grid: self.tile_grid[0] = self.frame_index

    def _fade_leds_to(self, color):
        self.target_color = list(color)

    def _fade_leds(self):
        # Helper
        changed = False
        for i in range(3): # R, G, B
            if self.current_color[i] < self.target_color[i]:
                self.current_color[i] = min(self.target_color[i], self.current_color[i] + self.fade_speed)
                changed = True
            elif self.current_color[i] > self.target_color[i]:
                self.current_color[i] = max(self.target_color[i], self.current_color[i] - self.fade_speed)
                changed = True

        if changed:
            # Apply to Onboard
            self.pixel_onboard.fill(tuple(self.current_color))
            self.pixel_onboard.write()
            # Apply to Strip
            self.pixel_strip.fill(tuple(self.current_color))
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
