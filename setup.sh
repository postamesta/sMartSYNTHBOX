#!/bin/bash
# setup.sh — bootstrap per sMart SynthBox
# auto installer, no user input

set -euo pipefail

echo "=== sMart SynthBox by Emanuele Martorelli — AUTO SETUP ==="

TARGET_DIR="/home/pi/synthbox"
REPO_URL="https://github.com/postamesta/smartsynthbox"

echo "Removing old folder if exists..."
sudo rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"
sudo chown -R pi:pi "$TARGET_DIR"

echo "Cloning repository GitHub into synthbox folder"
git clone --depth 1 "$REPO_URL" "$TARGET_DIR"

echo "Check authorization"
sudo chown -R pi:pi "$TARGET_DIR"
chmod -R u+rwX "$TARGET_DIR"

cd "$TARGET_DIR"

echo "Unlock install.sh"
chmod +x install.sh

echo "Open installer..."
sudo ./install.sh
