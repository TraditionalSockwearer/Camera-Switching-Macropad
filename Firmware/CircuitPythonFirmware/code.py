import board
import busio
import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC, make_key
from kmk.scanners.keypad import KeysScanner
from movie_extension import MovieExtension


displayio.release_displays()

# SCL=D5, SDA=D4
i2c = busio.I2C(board.D5, board.D4)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)

display = adafruit_displayio_ssd1306.SSD1306(
    display_bus, width=128, height=32
)


keyboard = KMKKeyboard()

# display extension
movie_ext = MovieExtension(display=display)
keyboard.extensions.append(movie_ext)

# KEY FUNCTIONS
def press_0(key, keyboard, *args):
    movie_ext.play_animation("CAM 1")
    keyboard.tap_key(KC.A)

def press_1(key, keyboard, *args):
    movie_ext.play_animation("CAM 2")
    keyboard.tap_key(KC.B)

def press_2(key, keyboard, *args):
    movie_ext.play_animation("CAM 3")
    keyboard.tap_key(KC.C)

def press_3(key, keyboard, *args):
    movie_ext.play_animation("CAM 4")
    keyboard.tap_key(KC.D)

# KEYMAP
CUST_A = make_key(names=('CAM_1',), on_press=press_0)
CUST_B = make_key(names=('CAM_2',), on_press=press_1)
CUST_C = make_key(names=('CAM_3',), on_press=press_2)
CUST_D = make_key(names=('CAM_4',), on_press=press_3)

keyboard.matrix = KeysScanner(
    pins=(board.D0, board.D1, board.D2, board.D3),
    value_when_pressed=False,
    pull=True,
)

keyboard.keymap = [
    [CUST_A, CUST_B, CUST_C, CUST_D],
]

if __name__ == '__main__':
    keyboard.go()
