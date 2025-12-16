# Custom OBS Macropad (RP2040) - Work in Progress

![Status](https://img.shields.io/badge/Status-In_Development-orange)
![Hardware](https://img.shields.io/badge/Hardware-Seeed_XIAO_RP2040-blue)
![Software](https://img.shields.io/badge/Firmware-MicroPython-yellow)

## Project Status: Active Development
**Current Phase:** PCB Design & Firmware Simulation
This project is currently in the prototyping phase. The firmware logic has been partially validated via simulation (Wokwi), and the parts are currently being delivered. 

## Project Overview
This project is an ongoing engineering initiative to build a custom, 4-key mechanical macropad designed specifically for **Live OBS (Open Broadcaster Software) Scene Switching**.

**The Use Case:**
This device is being built for a local temple's media team. The goal is to provide volunteer operators with a simplified, fail-safe hardware interface to switch camera angles during live services, eliminating the need to interact with complex software UI during a broadcast.

## Planned Features
* **Context-Aware Display:** Integrated **0.91" OLED** to display active camera scenes ("Camera 1 Active", etc.).
* **Synced RGB Feedback:** 4x **SK6812 Mini-E LEDs** that provide colour-coded status indicators synchronised with the active scene.
* **USB HID Interface:** Acts as a standard keyboard sending F13-F24 keys to trigger OBS hotkeys.
* **Compact Form Factor:** Custom 3D-printed enclosure with heat-set inserts for durability.

## Tech Stack
* **Microcontroller:** Seeed Studio XIAO RP2040
* **EDA / PCB:** KiCad 7.0
* **CAD:** Fusion 360
* **Firmware:** Python (MicroPython) with State Machine logic.
* **Simulation:** Wokwi (Used to validate I2C OLED & NeoPixel logic).

## Development Roadmap
- [x] **Requirement Analysis:** Defined constraints (silent switches, OLED feedback).
- [x] **Component Sourcing:** Validated BOM (Bill of Materials) for cost/availability.
- [x] **Schematic Capture:** Completed electrical schematic in KiCad.
- [x] **PCB Layout:** Routing tracks and defining edge cuts (In Progress).
- [ ] **Prototyping:** 3D printing the case and soldering the first unit.
- [ ] **Firmware Prototype:** Created state-machine logic in Wokwi (Simulation).
- [ ] **Integration:** Final HID implementation and OBS setup at the venue.

## Repository Structure
```text
/CAD          # STL files (In Progress)
/PCB       # Schematic and PCB files
/Firmware     # Wokwi simulation code and future main.py
```



## CAD Model
<img width="951" height="779" alt="image" src="https://github.com/user-attachments/assets/b5844305-660c-411d-9da0-f54c886693f1" />

<img width="984" height="730" alt="image" src="https://github.com/user-attachments/assets/2d7f6ce6-2620-40b6-8b80-b89ede5abe7f" />

<img width="1006" height="647" alt="image" src="https://github.com/user-attachments/assets/8a1b63fc-cbfb-4a23-8d46-a5110c560c23" />

Made in Fusion360


## PCB
<img width="1146" height="620" alt="image" src="https://github.com/user-attachments/assets/fefac079-6841-43f9-895a-d0292b97b4ad" />

## Schematic

<img width="764" height="378" alt="image" src="https://github.com/user-attachments/assets/d3047c62-dad2-44fa-a111-7360c529ee98" />

# BOM

* 4x Cherry MX Switches 

* 2x SK6812 MINI Leds

SK6812 MINI-E RGB 20PCS Link: 

    https://www.aliexpress.com/item/1005008308801366.html

* 1x XIAO RP2040 

Seeed XIAO RP2040 Link: 

    https://www.aliexpress.com/item/1005008200917480.html

* 4x Blank DSA Keycaps

Blank Keycaps 10PCS Link: 
    
    https://www.aliexpress.com/item/1005005514406952.html

* 4x M3x16 Bolt 

M3x16mm Screw Link: 
    
    https://www.aliexpress.com/item/1005008585550992.html

* 4x M3 Heatset 

M3 Heat Set Link: 

    https://www.aliexpress.com/item/1005008897571758.html

* 1x 0.91" 128x32 OLED Display 

OLED Display Link: 

    https://www.aliexpress.com/item/1005008640108394.html

* 1x Case (2 parts: Bottom Case and Cover)

* 1x PCB

I used JLBPCB for PCB
Gerber files are made by opening pcb file. Then press the Files, then Plot, and make sure to press drill and as a single file (it's an option)

