sMart SYNTHBOX – Raspberry Pi Headless SoundFont Player
=======================================================

Author: Emanuele Martorelli (postamesta@yahoo.com)
Coding: GPT-5
Based on: Fluidsynth under LGPL license
Version: 1.0  
Language: English  

Description:
------------
sMart SynthBox turns your Raspberry Pi into a standalone plug-and-play
MIDI SoundFont player (sfz/sf2) with display navigation.


Requirements:
-------------
• Raspberry Pi OS Lite (latest)
• Raspberry Pi4 with Pimoroni Audio Pirate (e.g. HiFiBerry DAC SPI displ ST7789 240x240)
• USB MIDI keyboard
• Internet connection (for first installation only)

BUTTONS
A = previous soundfont
B = next soundfont
Y = load soundfont
X (hold 6 seconds) = shutdown

DEFAULT SOUNDFONT NOT PRESENT
- At the message "No soundfonts found"
Place additional SoundFonts inside /home/pi/synthbox/sounds

FEATURES
- ST7789 240x240 display menu
- SoundFont selection
- MIDI auto-detection
- FluidSynth auto-launch
- Shutdown button

Installation:
-------------
1. Flash Raspberry Pi OS Lite onto an SD card.
2. Boot and connect to your network.
3. Copy the “synthbox” folder to /home/pi
4. Enter in folder synthbox with prompt:
   cd /home/pi/synthbox
5. Run installer:
   chmod +x install.sh
   sudo ./install.sh
System will reboot and start SynthBox automatically

The installation will:
 - install all dependencies (Python, FluidSynth, ALSA utils)
 - install the Pimoroni ST7789 display driver
 - create the service synthbox.service (auto-start at boot)
 - download FluidR3_GM.sf2 into /home/pi/synthbox/sounds

Usage:
------
Just boot your Raspberry Pi.
The display will show available SoundFonts.
Use buttons to navigate and select.
Once selected, connect your USB MIDI keyboard and play!

Important: if your keyboard is not recognized: 
- unplug 
- double press Y key
- wait for the message "Waiting for Midi" and plug again.

Notes:
------
• SoundFont folder: /home/pi/synthbox/sounds
• You can add more .sf2 files there with drag&drop.

Note: FluidSynth is free software distributed under the GNU
Lesser General Public License (LGPL), allowing for both modification
and use in commercial or closed-source applications, as long as 
certain conditions are met. The original copyright is from 2000-2024 
by Peter Hanappe and others

sMart SYNTHBOX by Emanuele Martorelli is tested on a
Raspberry Pi4 with Pimoroni Audio Pirate Headphones.
Enjoy your standalone SynthBox!
