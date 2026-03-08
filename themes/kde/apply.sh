#!/bin/bash
set -euo pipefail
THEME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install KDE color scheme
mkdir -p "$HOME/.local/share/color-schemes"
cp "$THEME_DIR/linta.colors" "$HOME/.local/share/color-schemes/Linta.colors"

# Apply via plasma-apply-colorscheme (if available)
if command -v plasma-apply-colorscheme &>/dev/null; then
    plasma-apply-colorscheme Linta
fi

echo "Linta KDE theme applied."
