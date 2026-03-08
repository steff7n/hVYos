#!/bin/bash
set -euo pipefail
RICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

mkdir -p "$CONFIG_HOME"/{waybar,mako,fuzzel,swaylock}
cp "$RICE_DIR/waybar/config.jsonc" "$CONFIG_HOME/waybar/config.jsonc"
cp "$RICE_DIR/waybar/style.css" "$CONFIG_HOME/waybar/style.css"
cp "$RICE_DIR/mako/config" "$CONFIG_HOME/mako/config"
cp "$RICE_DIR/fuzzel/fuzzel.ini" "$CONFIG_HOME/fuzzel/fuzzel.ini"
cp "$RICE_DIR/swaylock/config" "$CONFIG_HOME/swaylock/config"

pkill -SIGUSR2 waybar 2>/dev/null || true
makoctl reload 2>/dev/null || true

echo "Rice 'Ember' applied."
