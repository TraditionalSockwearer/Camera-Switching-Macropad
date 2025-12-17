import displayio
import terminalio
import time
from adafruit_display_text import label
from kmk.extensions import Extension
from movie_data import FRAMES

class MovieExtension(Extension):
    def __init__(self, display):
        self.display = display

        self.is_playing = False
        self.last_tick = 0
        self.frame_index = 0
        self.target_text = "READY"

        self.main_group = displayio.Group()
        self.anim_group = displayio.Group()
        self.text_group = displayio.Group()

        total_frames = len(FRAMES)
        self.bitmap = displayio.Bitmap(32, 32 * total_frames, 2)

        for f_idx, frame_bytes in enumerate(FRAMES):
            if len(frame_bytes) < 128:
                missing = 128 - len(frame_bytes)
                frame_bytes += b'\x00' * missing
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
        #Graphics
        self.text_area = label.Label(
            terminalio.FONT,
            text="READY",
            color=0xFFFFFF,
            scale=2,
            x=34, y=10
        )
        self.text_group.append(self.text_area)

        # 4. Attach Groups to Display
        self.main_group.append(self.text_group)
        self.display.root_group = self.main_group

    def play_animation(self, text_after):
        if self.is_playing: return

        self.target_text = text_after
        self.frame_index = 0
        self.is_playing = True
        self.last_tick = time.monotonic()

        # Swap to Animation
        while len(self.main_group) > 0: self.main_group.pop()
        self.main_group.append(self.anim_group)

    def before_matrix_scan(self, sandbox):
        if self.is_playing:
            now = time.monotonic()
            if now - self.last_tick > 0.042:
                self.last_tick = now
                self.frame_index += 1

                if self.frame_index >= len(FRAMES):
                    self.is_playing = False

                    # Update Text & Recentering Logic
                    if self.text_area:
                        self.text_area.text = self.target_text
                        char_width = 12
                        new_x = max(2, (128 - (len(self.target_text) * char_width)) // 2)
                        self.text_area.x = int(new_x)
                    while len(self.main_group) > 0: self.main_group.pop()
                    self.main_group.append(self.text_group)
                else:
                    if self.tile_grid: self.tile_grid[0] = self.frame_index

    def on_runtime_enable(self, sandbox): pass
    def on_runtime_disable(self, sandbox): pass
    def during_bootup(self, keyboard): return
    def after_matrix_scan(self, sandbox): pass
    def before_hid_send(self, sandbox): pass
    def after_hid_send(self, sandbox): pass
    def on_powersave_enable(self, sandbox): pass
    def on_powersave_disable(self, sandbox): pass
