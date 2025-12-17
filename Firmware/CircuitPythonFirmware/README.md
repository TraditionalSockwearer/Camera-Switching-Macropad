# The Firmware (KMK + Animated OLED + NeoPixels)
Firmware built on the **Seeed Studio XIAO RP2040** running **CircuitPython** and **KMK Firmware**. It features a 128x32 OLED screen that plays animations when keys are pressed and syncs RGB lighting to the active camera state (Green, Red, Blue, Yellow).

## Feature Status
- [x] **4-Key Matrix Scanning** (KMK Firmware)
- [x] **OLED Support** (SSD1306 via I2C at 0x3C)
- [x] **Custom Animation Extension** (Non-blocking background playback)
- [x] **Responsive Text** (Auto-centering text labels like "CAM 1")
- [x] **RGB LED Sync** (Smooth non-blocking color fades matching the camera state)
- [x] **Onboard LED Control** (Syncs XIAO onboard NeoPixel with external strip)

## Hardware
* **Microcontroller:** Seeed Studio XIAO RP2040
* **Display:** 0.91" OLED (SSD1306 Driver, 128x32 resolution)
* **LEDs:**
    * 1x Onboard WS2812 (NeoPixel)
    * 4x SK6812MINI-E (External Strip connected to Pin D6)
* **Switches:** 4x Mechanical Switches (Directly wired to Pins D0, D1, D2, D3)

## Libraries Used
The following libraries must be installed in the `lib` folder on your `CIRCUITPY` drive:

| Library | Purpose |
| :--- | :--- |
| **KMK Firmware** | Core keyboard firmware handling matrix scanning and keycodes. |
| **adafruit_displayio_ssd1306** | Driver for the OLED display. |
| **adafruit_display_text** | Handles text rendering and label positioning on screen. |
| **adafruit_bus_device** | Core I2C communication helper. |
| **neopixel** | Controls the addressable RGB LEDs. |

> **Note:** Using **CircuitPython 9.x or 10.x** requires built-in library `i2cdisplaybus`.

## 📂 File Structure
`CIRCUITPY` drive should look like this:

```text
CIRCUITPY/
├── lib/
│   ├── kmk/
│   ├── adafruit_display_text/
│   ├── adafruit_displayio_ssd1306.mpy
│   ├── adafruit_bus_device/
│   └── neopixel.mpy
├── code.py              # Main entry point (Keyboard setup)
├── movie_extension.py   # Custom extension for Animation & LEDs
└── movie_data.py        # Raw bitmap data for the animation
