#!/bin/bash
# install_no_autosf.sh
# Installer per sMart SynthBox (NO automatic SoundFont)
# Usalo in /home/pi/synthbox come: sudo bash install_no_autosf.sh

set -euo pipefail

echo "=== Installing sMart SynthBox (NO AUTO-SOUNDFONT) ==="

# Assicuriamoci di lavorare nella cartella giusta
cd /home/pi/synthbox || { echo "/home/pi/synthbox not found. Put project here and retry."; exit 1; }

echo "Fixing ownership to pi:pi..."
sudo chown -R pi:pi /home/pi/synthbox || true

# Rinomina eventuali cartelle con CRLF residuo create su Windows
mv "fonts"$'\r' fonts 2>/dev/null || true
mv "sounds"$'\r' sounds 2>/dev/null || true

echo "Updating package lists..."
sudo apt-get update -y

echo "Installing required packages (may install many dependencies)..."
sudo apt-get install -y git python3 python3-pip python3-pil \
    python3-rpi.gpio python3-spidev fluidsynth alsa-utils wget unzip dos2unix || true

echo "Converting project files to Unix format (safe)..."
dos2unix install.sh main.py shutdown.sh synthbox.service README.txt 2>/dev/null || true

# Enable SPI via raspi-config non-interactive (if raspi-config exists)
if command -v raspi-config >/dev/null 2>&1; then
    echo "Enabling SPI (raspi-config nonint)..."
    sudo raspi-config nonint do_spi 0 || true
else
    echo "raspi-config not found — please enable SPI manually if required."
fi

# Ensure config.txt modifications are applied for both common locations
apply_cfg () {
  local CFG="$1"
  if [ -f "$CFG" ]; then
    echo "Ensuring SPI and HiFiBerry overlay in $CFG ..."
    sudo sed -i '/dtoverlay=hifiberry-dac/d' "$CFG" 2>/dev/null || true
    sudo sed -i '/dtparam=spi=on/d' "$CFG" 2>/dev/null || true
    # append only once
    echo "dtparam=spi=on" | sudo tee -a "$CFG" >/dev/null
    echo "dtoverlay=hifiberry-dac" | sudo tee -a "$CFG" >/dev/null
  fi
}
apply_cfg /boot/firmware/config.txt
apply_cfg /boot/config.txt

echo "Stopping/disabling any system/user fluidsynth instances to avoid conflicts..."
sudo systemctl disable --now fluidsynth.service 2>/dev/null || true
sudo systemctl stop fluidsynth.service 2>/dev/null || true
# user units
systemctl --user stop fluidsynth.service 2>/dev/null || true
systemctl --user disable fluidsynth.service 2>/dev/null || true
rm -f /etc/systemd/user/default.target.wants/fluidsynth.service 2>/dev/null || true
rm -f /etc/xdg/systemd/user/default.target.wants/fluidsynth.service 2>/dev/null || true
rm -f ~/.config/systemd/user/default.target.wants/fluidsynth.service 2>/dev/null || true
sudo killall fluidsynth 2>/dev/null || true

echo "Installing ST7789 Python driver (will try pip, fallback to git if needed)..."
# try pip then fallback
if ! sudo pip3 install st7789 --break-system-packages 2>/dev/null; then
    sudo pip3 install git+https://github.com/pimoroni/st7789-python --break-system-packages
fi

echo "Preparing folders (sounds/fonts) and fixing permissions..."
mkdir -p /home/pi/synthbox/sounds
mkdir -p /home/pi/synthbox/fonts
sudo chown -R pi:pi /home/pi/synthbox
chmod -R 755 /home/pi/synthbox

echo "NOTE: This installer does NOT download or install any SoundFont."
echo "Place your .sf2/.sf3 files into /home/pi/synthbox/sounds (via SCP/USB/drag&drop)."

echo "Installing systemd service (synthbox.service)..."
if [ -f synthbox.service ]; then
    sudo cp synthbox.service /etc/systemd/system/synthbox.service
    sudo dos2unix /etc/systemd/system/synthbox.service 2>/dev/null || true
    sudo systemctl daemon-reload
    sudo systemctl enable synthbox.service
else
    echo "WARNING: synthbox.service not found in current folder — service not installed."
fi

# Create a safe asound.conf to prefer hifiberry (if present) — harmless otherwise
echo "Creating /etc/asound.conf to prefer sndrpihifiberry if present..."
sudo tee /etc/asound.conf >/dev/null <<'EOF'
pcm.!default {
  type plug
  slave.pcm "hw:sndrpihifiberry,0"
}
ctl.!default {
  type hw
  card sndrpihifiberry
}
EOF

echo "Final permission fix (synthbox folder writable by pi)..."
sudo chown -R pi:pi /home/pi/synthbox
chmod -R u+rwX /home/pi/synthbox

echo "INSTALLER COMPLETE."
echo "Reboot is recommended to apply /boot/config.txt changes and start the synthbox.service."
sudo reboot now