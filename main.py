#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, time, subprocess, threading
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import st7789

# === Paths ===
BASE_DIR = "/home/pi/synthbox"
SOUND_DIR = os.path.join(BASE_DIR, "sounds")
FONT_PATH = os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf")
SHUTDOWN_SCRIPT = os.path.join(BASE_DIR, "shutdown.sh")

# === Variables ===
HOLD_TIME = 6
BTN_A = 5
BTN_B = 6
BTN_X = 16
BTN_Y = 24

AUDIO_DEVICE = "plughw:CARD=sndrpihifiberry,DEV=0"
DEFAULT_SF = "/home/pi/synthbox/sounds/FluidR3_GM.sf2"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in (BTN_A, BTN_B, BTN_X, BTN_Y):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# === Display ST7789 ===
disp = st7789.ST7789(
    height=240, width=240, rotation=90,
    port=0, cs=1, dc=9, backlight=13, spi_speed_hz=80000000
)
disp.begin()

# === Font ===
try:
    font = ImageFont.truetype(FONT_PATH, 18)
except Exception:
    font = ImageFont.load_default()

# === SoundFonts ===
try:
    sf_files = sorted([f for f in os.listdir(SOUND_DIR) if f.lower().endswith((".sf2", ".sfz"))])
except Exception:
    sf_files = []
if not sf_files:
    sf_files = ["(no soundfonts found)"]

index = 0
fluidsynth_proc = None
shutdown_lock = threading.Lock()

# === Display ===
def draw_menu(selected, msg=None):
    img = Image.new("RGB", (240, 240), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 6), "sMart SynthBox", font=font, fill=(255, 255, 0))
    y = 38
    for i, name in enumerate(sf_files):
        color = (0, 255, 0) if i == selected else (180, 180, 180)
        draw.text((10, y), name, font=font, fill=color)
        y += 26
        if y > 200:
            break
    if msg:
        draw.text((10, 210), msg, font=font, fill=(100, 255, 255))
    disp.display(img)

# === FluidSynth ===
def stop_sf():
    global fluidsynth_proc
    if fluidsynth_proc:
        try:
            fluidsynth_proc.terminate()
            fluidsynth_proc.wait(timeout=2)
        except Exception:
            try:
                fluidsynth_proc.kill()
            except Exception:
                pass
        fluidsynth_proc = None

def ensure_fs_port(timeout=10):
    for i in range(timeout):
        try:
            out = subprocess.check_output(["aconnect", "-o"]).decode()
            if "FLUID" in out or "Synth input port" in out:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def connect_midi_auto(max_wait=10):
    for i in range(max_wait):
        try:
            ports = subprocess.check_output(["aconnect", "-i"]).decode()
            for line in ports.splitlines():
                if ("Keystation" in line or "MIDI" in line) and "Through" not in line:
                    client = line.split()[1].replace(":", "")
                    try:
                        subprocess.call(["aconnect", f"{client}:0", "128:0"])
                        return f"MIDI linked ({client}:0)"
                    except Exception:
                        pass
        except Exception:
            pass
        time.sleep(1)
    return "No MIDI"

def play_sf_with_auto_connect(sf_path):
    global fluidsynth_proc
    stop_sf()
    if not os.path.exists(sf_path):
        draw_menu(0, "SF missing!")
        return
    cmd = [
        "fluidsynth",
        "-a", "alsa",
        "-m", "alsa_seq",
        "-o", f"audio.alsa.device={AUDIO_DEVICE}",
        "-o", "synth.sample-rate=44100",
        sf_path
    ]
    try:
        fluidsynth_proc = subprocess.Popen(cmd)
        if ensure_fs_port(10):
            msg = connect_midi_auto(max_wait=8)
            draw_menu(index, msg)
        else:
            draw_menu(index, "FS port missing")
    except Exception as e:
        draw_menu(index, "FS start error")
        print("Error launching FluidSynth:", e)

# === Shutdown ===
def do_shutdown():
    with shutdown_lock:
        stop_sf()
        try:
            disp.display(Image.new("RGB", (240,240), (0,0,0)))
        except Exception:
            pass
        try:
            subprocess.call([SHUTDOWN_SCRIPT])
        except Exception:
            pass

def handle_hold(pin):
    start = time.time()
    while GPIO.input(pin) == GPIO.LOW:
        time.sleep(0.1)
        if pin == BTN_X and (time.time() - start) >= HOLD_TIME:
            draw_menu(index, "Shutting down...")
            do_shutdown()
            return

# === Command Keys ===
def button_pressed_poll(pin):
    global index
    threading.Thread(target=handle_hold, args=(pin,), daemon=True).start()
    time.sleep(0.12)
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
        if sel and not sel.startswith("("):
            play_sf_with_auto_connect(os.path.join(SOUND_DIR, sel))
        draw_menu(index)

# === Main loop ===
def main():
    draw_menu(index)
    if not os.path.exists(DEFAULT_SF):
        draw_menu(index, "Missing SoundFont!")
        print("ERROR: SoundFont not found at", DEFAULT_SF)
        while True:
            time.sleep(1)
    prev = {BTN_A:1, BTN_B:1, BTN_X:1, BTN_Y:1}
    try:
        print("SynthBox running (GPIO polling active)...")
        while True:
            for p in (BTN_A, BTN_B, BTN_X, BTN_Y):
                val = GPIO.input(p)
                if val == GPIO.LOW and prev[p] == 1:
                    button_pressed_poll(p)
                prev[p] = val
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        stop_sf()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
