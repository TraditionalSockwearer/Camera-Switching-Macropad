# OBS & Media Macropad (RP2040)

A custom automated macropad built with a custom PCB and RP2040, featuring dual modes for **OBS Camera Switching** and **Media Control** with scrolling track info and animated OLED feedback.

## Features

- **Dual Modes**: Switch between OBS and Media modes via a menu.
- **OLED Display**: Shows current mode, active camera, or scrolling song title with animations.
- **OBS Mode**:
  - 4 Camera Buttons (Green, Red, Blue, Yellow LEDs).
  - Animated film reel transition between camera switches.
  - **Hold Button 4 (Last Button)** (2s) to exit to Menu.
  - Input blocking prevents accidental spamming during animations.
- **Media Mode**:
  - Controls: Previous, Play/Pause, Next, Mute.
  - Custom animations for each action (Skip, Play/Pause, Mute/Unmute).
  - **Hold Button 2 (Play/Pause)** (2s) to exit to Menu.
  - **Scrolling Text**: Displays the currently playing song from your PC (requires host script).

## Setup

### 1. Firmware

1. Flash CircuitPython to your RP2040.

2. Copy the **entire contents** of `Firmware/CircuitPy Drive` to the root of your `CIRCUITPY` drive.
   - This folder contains pre-compiled `.mpy` files ready to use.
   - Structure:
     ```
     CIRCUITPY/
     ├── boot.py
     ├── code.py
     └── lib/
         ├── kmk/           (Keyboard library)
         ├── main_logic.mpy
         ├── movie_data.mpy
         ├── movie_extension.mpy
         └── (other dependencies)
     ```

3. If you want to modify the firmware, edit the source files in `Firmware/CircuitPythonFiles/` and recompile using `mpy-cross`.

### 2. Host Script (For Media Info)

> **Note**: Python 3.12 is recommended. If you have connection issues, ensure you are using the correct COM port and that the device lists a VID of 0x2886.

To see your PC's currently playing song on the OLED:

1. Open this folder in a terminal.

2. Install requirements:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the communication script:

    ```bash
    py host_media_bridge.py
    ```

4. Switch the macropad to Media Mode.

## Usage

**Menu**:

- **Btn 1**: OBS Mode
- **Btn 2**: Media Mode

**Input Layout**:

| Button | OBS Mode | Media Mode |
| :--- | :--- | :--- |
| **1** | Camera 1 | Previous |
| **2** | Camera 2 | Play/Pause (Hold to Exit) |
| **3** | Camera 3 | Next |
| **4** | Camera 4 (Hold to Exit) | Mute |

## Folder Structure

| Folder | Description |
| :--- | :--- |
| `Firmware/CircuitPy Drive/` | Pre-compiled files ready to copy to CIRCUITPY |
| `Firmware/CircuitPythonFiles/` | Source `.py` files for development |
| `Animation From wokwi/` | Original animation source files (.ino) |

## Hardware

- RP2040 Microcontroller
- SSD1306 OLED (128x32)
- 4x Mechanical Switches
- NeoPixel LEDs
