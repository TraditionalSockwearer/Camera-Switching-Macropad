"""
Macropad
"""

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import neopixel 
import utime

WIDTH  = 128
HEIGHT = 64
SCL_PIN = 27
SDA_PIN = 26  
BTN_PINS = [15, 14, 13, 12] 
LED_PIN = 7     
NUM_LEDS = 4 

FADE_STEPS = 20     # Higher = Smoother
FADE_DELAY = 0.01   # Delay between steps

COLORS = [
    (0, 255, 0),    # Cam 1: All Green
    (255, 0, 0),    # Cam 2: All Red
    (0, 0, 255),    # Cam 3: All Blue
    (255, 255, 0)   # Cam 4: All Yellow
]

def init_hardware():
    i2c = I2C(1, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
    
    buttons = []
    for p in BTN_PINS:
        buttons.append(Pin(p, Pin.IN, Pin.PULL_UP))

    leds = neopixel.NeoPixel(Pin(LED_PIN), NUM_LEDS)
    return oled, buttons, leds

def animate_sync_fade(leds, target_color):

    start_r, start_g, start_b = leds[0]
    target_r, target_g, target_b = target_color
    
    for step in range(1, FADE_STEPS + 1):
        fraction = step / FADE_STEPS
        
        r = int(start_r + (target_r - start_r) * fraction)
        g = int(start_g + (target_g - start_g) * fraction)
        b = int(start_b + (target_b - start_b) * fraction)
        
        leds.fill((r, g, b)) 
        leds.write()
        
        utime.sleep(FADE_DELAY)

def update_status(oled, leds, active_cam):
    # A. Update Screen
    oled.fill(0)
    oled.text("OBS MACROPAD", 10, 0)
    oled.hline(0, 10, 128, 1) 
    oled.text(f"Camera {active_cam} Active", 5, 30)
    
    # Draw box
    x_pos = 5 + ((active_cam - 1) * 30)
    oled.fill_rect(x_pos, 45, 20, 10, 1)
    oled.show()

    # Get the color for this camera
    new_color = COLORS[active_cam - 1]
    
    print(f"Fading all LEDs to Camera {active_cam} Color...")
    animate_sync_fade(leds, new_color)


def main():
    oled, buttons, leds = init_hardware()
    
    oled.text("System Ready.", 5, 0)
    oled.show()
    
    # Start with all LEDs off
    leds.fill((0,0,0))
    leds.write()
    
    # Startup Flash (White)
    utime.sleep(0.5)
    animate_sync_fade(leds, (50, 50, 50))
    animate_sync_fade(leds, (0, 0, 0))

    current_state = 0 

    while True:
        for i in range(4):
            if buttons[i].value() == 0:
                cam_id = i + 1 
                
                if current_state != cam_id:
                    current_state = cam_id
                    update_status(oled, leds, current_state)
                
                utime.sleep(0.1) 

        utime.sleep(0.05)

if __name__ == '__main__':
    main()