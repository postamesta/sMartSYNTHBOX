sMart SYNTHBOX – Raspberry Pi Headless SoundFont Player
=======================================================
by Emanuele Martorelli. A simple MIDI soundfont player
for your Raspberry PI4 to turn your controller into a synth

<img width="1200" height="675" alt="Image" src="https://github.com/user-attachments/assets/1cb0d5e7-c326-451d-939a-e064754c5c81" />

Version: 1.0 - First release can play only individual .sfz or .sf2
files or the FIRST PRESET of every multiple soundont. In the next
update it will be possivle to navigate through presets.

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
A = previous soundfont\n
B = next soundfont\n
Y = load soundfont\n
X (hold 6 seconds) = shutdown

Fast install:

1. Flash Raspberry Pi OS Lite onto an SD card.
2. Insert the card in your Raspberry PI 4 and boot.
3. Open a terminal emulator from computer,
connect with Host name/ip address:
192.168.1.117
port: 22
4. Run command from prompt:
curl -sSL https://raw.githubusercontent.com/postamesta/smartsynthbox/main/setup.sh | bash
