#!/bin/bash
set -e
echo "Starting SynthBox installer..."

sudo apt-get update -y
sudo apt-get install -y fluidsynth alsa-utils python3-pil python3-rpi.gpio python3-numpy wget unzip git dpkg

# pip st7789 if needed
if ! python3 -c "import st7789" 2>/dev/null; then
  echo "Installing python st7789 via pip3 (may request --break-system-packages)"
  sudo pip3 install st7789 gpiodevice --break-system-packages || true
fi

# mask existing fluidsynth
sudo systemctl stop fluidsynth.service 2>/dev/null || true
sudo systemctl disable --now fluidsynth.service 2>/dev/null || true
sudo systemctl mask fluidsynth.service 2>/dev/null || true
sudo systemctl --user stop fluidsynth.service 2>/dev/null || true
sudo systemctl --user disable --now fluidsynth.service 2>/dev/null || true

mkdir -p /home/pi/synthbox/sounds
mkdir -p /home/pi/synthbox/fonts

SF_DEST="/home/pi/synthbox/sounds/FluidR3_GM.sf2"
if [ ! -f "$SF_DEST" ]; then
  TMPDEB="/tmp/fluid-sf.deb"
  wget -q -O "$TMPDEB" "https://ftp.us.debian.org/debian/pool/main/f/fluid-soundfont/fluid-soundfont-gm_3.1-5_all.deb" || true
  if [ -f "$TMPDEB" ]; then
    mkdir -p /tmp/fluid-sf
    dpkg-deb -x "$TMPDEB" /tmp/fluid-sf || true
    SF_FOUND=$(find /tmp/fluid-sf -type f -name "*.sf2" | head -n1)
    if [ -n "$SF_FOUND" ]; then
      cp "$SF_FOUND" "$SF_DEST" || true
      chown pi:pi "$SF_DEST" || true
      echo "SoundFont installed to $SF_DEST"
    else
      echo "Could not extract .sf2; please download FluidR3_GM.sf2 manually."
    fi
  else
    echo "Deb package not downloaded; please download FluidR3_GM.sf2 manually."
  fi
fi

# copy font placeholder if exists in package
if [ -f "./fonts/DejaVuSans.ttf" ]; then
  cp ./fonts/DejaVuSans.ttf /home/pi/synthbox/fonts/DejaVuSans.ttf || true
fi

# create systemd service
SERVICE_FILE="/etc/systemd/system/synthbox.service"
sudo bash -c "cat > $SERVICE_FILE" <<'EOF'
[Unit]
Description=SynthBox sMart - Fluidsynth Player
After=network.target sound.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/synthbox/main.py
Restart=on-failure
User=pi
WorkingDirectory=/home/pi/synthbox/
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo chmod 644 $SERVICE_FILE
sudo systemctl daemon-reload
sudo systemctl enable --now synthbox.service

echo "Install complete."
