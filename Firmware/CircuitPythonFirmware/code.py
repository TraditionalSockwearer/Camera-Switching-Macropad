import board
import busio
import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC, make_key
from kmk.scanners.keypad import KeysScanner
from kmk.modules.layers import Layers
from kmk.modules.holdtap import HoldTap
from kmk.extensions.media_keys import MediaKeys
from movie_extension import MovieExtension


displayio.release_displays()
i2c = busio.I2C(board.D5, board.D4)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

keyboard = KMKKeyboard()

# Extensions & Modules
movie_ext = MovieExtension(display=display)
keyboard.extensions.append(movie_ext)
keyboard.extensions.append(MediaKeys())

layers = Layers()
holdtap = HoldTap()
holdtap.tap_time = 2000
keyboard.modules.append(layers)
keyboard.modules.append(holdtap)


# --- LAYERS ---
LAYER_MENU = 0
LAYER_OBS = 1
LAYER_MEDIA = 2

# --- HELPERS ---
def switch_to_menu(key, keyboard, *args):
    keyboard.active_layers.clear()
    keyboard.active_layers.insert(0, LAYER_MENU)
    movie_ext.show_menu()

def switch_to_obs(key, keyboard, *args):
    keyboard.active_layers.clear()
    keyboard.active_layers.insert(0, LAYER_OBS)
    movie_ext.show_status("OBS MODE", (0, 255, 0))

def switch_to_media(key, keyboard, *args):
    keyboard.active_layers.clear()
    keyboard.active_layers.insert(0, LAYER_MEDIA)
    movie_ext.show_status("MEDIA MODE", (0, 0, 255))

# --- MEDIA HANDLERS ---
def media_pp(key, keyboard, *args):
    keyboard.tap_key(KC.MPLY)
    movie_ext.show_status("PLAY/PAUSE", (0, 255, 255))

def media_mute(key, keyboard, *args):
    keyboard.tap_key(KC.MUTE)
    movie_ext.show_status("MUTE", (255, 255, 255))

def media_prev(key, keyboard, *args):
    keyboard.tap_key(KC.MPRV)
    movie_ext.show_status("PREVIOUS", (255, 0, 255))

def media_next(key, keyboard, *args):
    keyboard.tap_key(KC.MNXT)
    movie_ext.show_status("NEXT", (255, 255, 0))


# --- OBS HANDLERS (With Blocking) ---
def press_0(key, keyboard, *args):
    if movie_ext.is_playing: return
    movie_ext.play_animation("CAM 1", (0, 255, 0))
    keyboard.tap_key(KC.A)

def press_1(key, keyboard, *args):
    if movie_ext.is_playing: return
    movie_ext.play_animation("CAM 2", (255, 0, 0))
    keyboard.tap_key(KC.B)

def press_2(key, keyboard, *args):
    if movie_ext.is_playing: return
    movie_ext.play_animation("CAM 3", (0, 0, 255))
    keyboard.tap_key(KC.C)

def press_3(key, keyboard, *args):
    if movie_ext.is_playing: return
    movie_ext.play_animation("CAM 4", (255, 255, 0))
    keyboard.tap_key(KC.D)


# --- KEYS ---
TO_OBS = make_key(names=('TO_OBS',), on_press=switch_to_obs)
TO_MEDIA = make_key(names=('TO_MED',), on_press=switch_to_media)
TO_MENU = make_key(names=('TO_MENU',), on_press=switch_to_menu)

CUST_A = make_key(names=('CAM_1',), on_press=press_0)
CUST_B = make_key(names=('CAM_2',), on_press=press_1)
CUST_C = make_key(names=('CAM_3',), on_press=press_2)
CUST_D = make_key(names=('CAM_4',), on_press=press_3)

# OBS Exit: Tap=Cam4, Hold (2s)=Menu
HT_BTN4 = KC.HT(CUST_D, TO_MENU)

MED_PP = make_key(names=('M_PP',), on_press=media_pp)
MED_MUTE = make_key(names=('M_MUTE',), on_press=media_mute)
MED_PRV = make_key(names=('M_PREV',), on_press=media_prev)
MED_NXT = make_key(names=('M_NEXT',), on_press=media_next)

MED_PP_EXIT = KC.HT(MED_PP, TO_MENU)


keyboard.matrix = KeysScanner(
    pins=(board.D3, board.D2, board.D1, board.D0),
    value_when_pressed=False,
    pull=True,
)

keyboard.keymap = [
    [TO_OBS, TO_MEDIA, KC.NO, KC.NO],
    [CUST_A, CUST_B, CUST_C, HT_BTN4],
    [MED_PRV, MED_PP_EXIT, MED_NXT, MED_MUTE]
]

if __name__ == '__main__':
    movie_ext.show_menu()
    keyboard.go()
