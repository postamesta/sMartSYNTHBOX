******************
* sMart SYNTHBOX *
******************

by Emanuele Martorelli
Nov 2025 - Plug & Play Edition

sMart SynthBox is a plug-and-play FluidSynth-based sampler designed for Raspberry Pi 4 with Pimoroni Audio Pirate Heaphone.  
It allows you to browse and load SoundFonts directly from a small display using simple buttons,  
and play them via any USB MIDI keyboard.

Quick start:
Format a Micro SD card and install Raspbian OS lite

1) Copy the 'synthbox' folder to /home/pi/.
2) On the Pi, run:
   cd /home/pi/synthbox
   sudo bash install.sh
3) Reboot if requested.
4) Use buttons: A=prev, B=next, Y=play/load, hold X=shutdown (6s).

Default SoundFont path:
  /home/pi/synthbox/sounds/FluidR3_GM.sf2

If the display shows 'Missing SoundFont!', check that the sf2 exists in that folder.

Important notes: 

1. If no keyboard is found double press on "Y" key on the Pimoroni Audio Pirate.
At the message "Waiting for midi" unplug and plug again the keyboard until is connected.

2. Font DejaVuSans.ttf must be placed in "font" folder.

3. Default soundfont FluidR3_GM.sf2 must be placed in "sounds" folder. This is the preset sound, that you can
easily edit by changing the following line in MAIN.PY file:

DEFAULT_SF = "/home/pi/synthbox/sounds/[your_soundfont_name.sf2]"


Credits:
Project: SynthBox sMart
Created by: Emanuele Martorelli & GPT-5 (OpenAI)
License: MIT
DejaVuSans font authors at: https://dejavu-fonts.github.io/Authors.html


# "sMart SynthBox” 
Plug & Play SoundFont Synthesizer for Raspberry Pi 4 and Pimoroni Pirate Audio Headphones

**Authors:**  
- Emanuele Martorelli (concept, hardware integration)  
- ChatGPT (OpenAI) * system orchestration, code development  

---

## Requirements
- Raspberry Pi 4
- Raspbian OS Lite with Python 3
- Pimoroni Pirate Audio Headphones (ST7789 240x240 SPI display or HifiBerry DAC compatible)
- USB MIDI Keyboard

---

## Installation

After installing Raspbian OS Lite on a micro SD

1. Copy the folder `synthbox` to `/home/pi/`
2. Install dependencies in prompt with command:
   
   sudo apt install python3-pil python3-rpi.gpio python3-st7789 fluidsynth
   
3. Enable the service:
   
   sudo cp install/synthbox.service /etc/systemd/system/
   sudo systemctl enable synthbox.service
   sudo systemctl start synthbox.service
   
4. Configure Wi-Fi:  
   
   sudo cp install/wpa_supplicant_template.conf /etc/wpa_supplicant/wpa_supplicant.conf
   sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
   
   Replace `[YOUR_WIFI_NAME]` and `[YOUR_WIFI_PASSWORD]` with your credentials.

---

## Usage
- Use **A/B** to browse SoundFonts  
- Double Press **Y** to load the selected one  
- Hold **X** (6 seconds) to safely shutdown  
- Connect your MIDI keyboard (auto-detected)

---

## Default SoundFont
Default file: `/home/pi/synthbox/sounds/FluidR3_GM.sf2`  
You can replace or add `.sf2` or `.sfz` files inside `/sounds`.

---

## Shutdown
Handled safely through `shutdown.sh`.

---

## Future Expansion
- Preset Explorer (navigate inside each SoundFont)
- OLED display support
- Custom MIDI CC mapping

---


Made with eagerness by **Emanuele Martorelli** & **ChatGPT**
