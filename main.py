#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, time, subprocess, threading
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import st7789

BASE_DIR = "/home/pi/synthbox"
SOUND_DIR = os.path.join(BASE_DIR, "sounds")
FONT_PATH = os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf")
SHUTDOWN_SCRIPT = os.path.join(BASE_DIR, "shutdown.sh")

HOLD_TIME = 6
BTN_A = 5
BTN_B = 6
BTN_X = 16
BTN_Y = 24

AUDIO_DEVICE = "plughw:CARD=sndrpihifiberry,DEV=0"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in (BTN_A, BTN_B, BTN_X, BTN_Y):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

disp = st7789.ST7789(
    height=240, width=240, rotation=90,
    port=0, cs=1, dc=9, backlight=13, spi_speed_hz=80000000
)
disp.begin()

try:
    font = ImageFont.truetype(FONT_PATH, 18)
except Exception:
    font = ImageFont.load_default()

sf_files = sorted([f for f in os.listdir(SOUND_DIR) if f.lower().endswith((".sf2", ".sfz"))])
if not sf_files:
    sf_files = ["(no soundfonts found)"]

index = 0
fluidsynth_proc = None
shutdown_lock = threading.Lock()

def draw_menu(selected, msg=None):
    img = Image.new("RGB", (240, 240), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 6), "sMart SynthBox", font=font, fill=(255, 255, 0))
    y = 40
    for i, name in enumerate(sf_files):
        color = (0, 255, 0) if i == selected else (180, 180, 180)
        draw.text((10, y), name, font=font, fill=color)
        y += 28
        if y > 200:
            break
    if msg:
        draw.text((10, 210), msg, font=font, fill=(0, 200, 255))
    disp.display(img)

def stop_sf():
    global fluidsynth_proc
    if fluidsynth_proc:
        try:
            fluidsynth_proc.terminate()
            fluidsynth_proc.wait(timeout=2)
        except Exception:
            fluidsynth_proc.kill()
        fluidsynth_proc = None

def connect_midi(max_wait=12):
    draw_menu(index, "Checking MIDI...")
    for i in range(max_wait):
        try:
            midi_ports = subprocess.check_output(["aconnect", "-i"]).decode()
            for line in midi_ports.splitlines():
                if "Keystation" in line or "MIDI" in line and "Through" not in line:
                    client_num = line.split()[1].replace(":", "")
                    subprocess.call(["aconnect", f"{client_num}:0", "128:0"])
                    msg = f"MIDI linked ({client_num}:0)"
                    draw_menu(index, msg)
                    return msg
        except:
            pass
        draw_menu(index, f"Waiting MIDI {i+1}s")
        time.sleep(1)
    draw_menu(index, "No MIDI device")
    return "No MIDI"

def play_sf(path):
    global fluidsynth_proc
    stop_sf()

    if not os.path.exists(path):
        draw_menu(index, "No SoundFont!")
        return

    cmd = [
        "fluidsynth",
        "-is",
        "-a", "alsa",
        "-m", "alsa_seq",
        "-o", "synth.sample-rate=44100",
        "-o", f"audio.alsa.device={AUDIO_DEVICE}",
        path
    ]

    fluidsynth_proc = subprocess.Popen(cmd)
    time.sleep(2)
    msg = connect_midi()
    draw_menu(index, msg)


def do_shutdown():
    with shutdown_lock:
        stop_sf()
        disp.display(Image.new("RGB", (240, 240), (0, 0, 0)))
        subprocess.call([SHUTDOWN_SCRIPT])

def handle_hold(pin):
    start = time.time()
    while GPIO.input(pin) == GPIO.LOW:
        time.sleep(0.1)
        if pin == BTN_X and (time.time() - start) >= HOLD_TIME:
            draw_menu(index, "Shutting down...")
            do_shutdown()
            return

def button_pressed(pin):
    global index
    threading.Thread(target=handle_hold, args=(pin,), daemon=True).start()
    time.sleep(0.15)
    if GPIO.input(pin) == GPIO.LOW:
        return

    if pin == BTN_A:
        index = (index - 1) % len(sf_files)
        draw_menu(index)

    elif pin == BTN_B:
        index = (index + 1) % len(sf_files)
        draw_menu(index)

    elif pin == BTN_Y:
        sel = sf_files[index]
        if not sel.startswith("("):
            play_sf(os.path.join(SOUND_DIR, sel))
        draw_menu(index)

def main():
    draw_menu(index)
    prev = {BTN_A: 1, BTN_B: 1, BTN_X: 1, BTN_Y: 1}

    try:
        while True:
            for p in (BTN_A, BTN_B, BTN_X, BTN_Y):
                val = GPIO.input(p)
                if val == GPIO.LOW and prev[p] == 1:
                    button_pressed(p)
                prev[p] = val
            time.sleep(0.05)
    finally:
        stop_sf()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
