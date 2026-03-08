#!/usr/bin/env python3
"""Generate visual HTML previews for all Linta themes.

Opens a browser with rendered mockups of each rice/theme showing
colors in context: status bar, notifications, launcher, terminal,
lock screen. No design skills required — just look and decide.

Usage:
    python3 scripts/preview-themes.py          # generate + open in browser
    python3 scripts/preview-themes.py --no-open # generate only
"""

from __future__ import annotations

import json
import sys
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NIRI_DIR = PROJECT_ROOT / "themes" / "niri"
KDE_DIR = PROJECT_ROOT / "themes" / "kde"
OUTPUT = PROJECT_ROOT / "build" / "output" / "theme-preview.html"


def load_rice(rice_dir: Path) -> dict | None:
    meta = rice_dir / "metadata.json"
    if not meta.exists():
        return None
    data = json.loads(meta.read_text())
    data["_dir"] = str(rice_dir)
    return data


def render_rice_card(theme: dict) -> str:
    c = theme["colors"]
    name = theme["name"]
    desc = theme.get("description", "")

    return f"""
    <div class="theme-card" style="background: {c['bg']}; border: 2px solid {c['border_active']};">
      <h2 style="color: {c['accent']}; margin: 0 0 4px 0;">{name}</h2>
      <p style="color: {c['fg_dim']}; margin: 0 0 16px 0; font-size: 13px;">{desc}</p>

      <!-- Status bar mockup -->
      <div class="bar" style="background: {c['bg']}ee; border-bottom: 2px solid {c['accent']};">
        <div class="bar-left">
          <span class="ws" style="color: {c['fg_dim']};">1</span>
          <span class="ws active" style="color: {c['accent']}; border-bottom: 2px solid {c['accent']};">2</span>
          <span class="ws" style="color: {c['fg_dim']};">3</span>
          <span class="ws" style="color: {c['fg_dim']};">4</span>
          <span style="color: {c['fg']}; margin-left: 12px;">~/Projects/linta</span>
        </div>
        <div class="bar-center" style="color: {c['fg']}; font-weight: bold;">14:32</div>
        <div class="bar-right" style="color: {c['fg']};">
          <span>  78%</span>
          <span style="margin-left: 10px;">  45%</span>
          <span style="margin-left: 10px;">  92%</span>
        </div>
      </div>

      <!-- Desktop area with terminal + notification -->
      <div class="desktop" style="background: {c['bg']};">
        <!-- Terminal mockup -->
        <div class="terminal" style="background: {c['bg_alt']}; border: 1px solid {c['border_inactive']};">
          <div class="term-titlebar" style="background: {c['bg']}; border-bottom: 1px solid {c['border_inactive']};">
            <span style="color: {c['fg_dim']};">foot — ~/Projects</span>
          </div>
          <div class="term-content">
            <span style="color: {c['accent']};">❯</span>
            <span style="color: {c['fg']};">lintactl info</span><br>
            <span style="color: {c['fg_dim']};">  Linta 25.1</span><br>
            <span style="color: {c['fg_dim']};">  Profile:    niri</span><br>
            <span style="color: {c['fg_dim']};">  Theme:      </span><span style="color: {c['accent']};">{name.lower()}</span><br>
            <span style="color: {c['fg_dim']};">  Kernel:     6.12.8</span><br>
            <span style="color: {c['green']};">  SELinux:    Enforcing</span><br><br>
            <span style="color: {c['accent']};">❯</span>
            <span style="color: {c['fg']};">git status</span><br>
            <span style="color: {c['green']};">  modified:   src/main.rs</span><br>
            <span style="color: {c['red']};">  deleted:    old_config.toml</span><br>
            <span style="color: {c['yellow']};">  new file:   README.md</span><br><br>
            <span style="color: {c['accent']};">❯</span>
            <span style="color: {c['fg']}; opacity: 0.6;">_</span>
          </div>
        </div>

        <!-- Notification mockup -->
        <div class="notification" style="background: {c['bg_alt']}; border: 2px solid {c['accent']}; border-radius: 8px;">
          <div style="color: {c['accent']}; font-weight: bold; margin-bottom: 4px;">System Update</div>
          <div style="color: {c['fg']}; font-size: 12px;">15 packages updated successfully.</div>
          <div style="color: {c['fg_dim']}; font-size: 11px; margin-top: 4px;">Snapshot #42 created.</div>
        </div>

        <!-- Launcher mockup -->
        <div class="launcher" style="background: {c['bg']}dd; border: 2px solid {c['accent']}; border-radius: 8px;">
          <div class="launcher-input" style="border-bottom: 1px solid {c['border_inactive']};">
            <span style="color: {c['accent']};">❯ </span>
            <span style="color: {c['fg']};">fire</span><span style="color: {c['fg']}; opacity: 0.3;">fox</span>
          </div>
          <div class="launcher-item selected" style="background: {c['bg_alt']};">
            <span style="color: {c['accent']};">Fire</span><span style="color: {c['fg']};">fox — Web Browser</span>
          </div>
          <div class="launcher-item">
            <span style="color: {c['fg_dim']};">Firewalld — Firewall Config</span>
          </div>
        </div>
      </div>

      <!-- Lock screen mockup -->
      <div class="lockscreen" style="background: {c['bg']};">
        <div class="lock-ring" style="border: 4px solid {c['accent']};">
          <div class="lock-inner" style="background: {c['bg_alt']}; color: {c['fg']};">14:32</div>
        </div>
      </div>

      <!-- Color palette swatches -->
      <div class="palette">
        <div class="swatch" style="background: {c['bg']};" title="bg: {c['bg']}"></div>
        <div class="swatch" style="background: {c['bg_alt']};" title="bg_alt: {c['bg_alt']}"></div>
        <div class="swatch" style="background: {c['fg']};" title="fg: {c['fg']}"></div>
        <div class="swatch" style="background: {c['accent']};" title="accent: {c['accent']}"></div>
        <div class="swatch" style="background: {c.get('accent2', c['accent'])};" title="accent2: {c.get('accent2', '')}"></div>
        <div class="swatch" style="background: {c['red']};" title="red: {c['red']}"></div>
        <div class="swatch" style="background: {c['green']};" title="green: {c['green']}"></div>
        <div class="swatch" style="background: {c['yellow']};" title="yellow: {c['yellow']}"></div>
        <div class="swatch" style="background: {c['blue']};" title="blue: {c['blue']}"></div>
      </div>
      <div class="hex-row" style="color: {c['fg_dim']};">
        <span>{c['bg']}</span>
        <span>{c['bg_alt']}</span>
        <span>{c['fg']}</span>
        <span>{c['accent']}</span>
        <span>{c.get('accent2', '')}</span>
        <span>{c['red']}</span>
        <span>{c['green']}</span>
        <span>{c['yellow']}</span>
        <span>{c['blue']}</span>
      </div>
    </div>
    """


def render_kde_card(theme: dict) -> str:
    c = theme["colors"]
    name = theme["name"]
    desc = theme.get("description", "")

    return f"""
    <div class="theme-card" style="background: {c['bg']}; border: 2px solid {c['accent']};">
      <h2 style="color: {c['accent']}; margin: 0 0 4px 0;">KDE: {name}</h2>
      <p style="color: {c['fg_dim']}; margin: 0 0 16px 0; font-size: 13px;">{desc}</p>

      <!-- KDE Panel mockup -->
      <div class="bar" style="background: {c['bg_alt']}; border-bottom: none;">
        <div class="bar-left">
          <span style="color: {c['accent']}; font-weight: bold;">Linta</span>
          <span style="color: {c['fg']}; margin-left: 16px;">Files</span>
          <span style="color: {c['fg']}; margin-left: 8px;">Terminal</span>
          <span style="color: {c['accent']}; margin-left: 8px;">Browser</span>
        </div>
        <div class="bar-center" style="color: {c['fg']}; font-weight: bold;">14:32</div>
        <div class="bar-right" style="color: {c['fg']};">
          <span>🔊</span>
          <span style="margin-left: 8px;">🔋</span>
          <span style="margin-left: 8px;">📶</span>
        </div>
      </div>

      <!-- KDE Desktop area -->
      <div class="desktop" style="background: {c['bg']};">
        <div class="kde-window" style="background: {c['bg_alt']}; border: 1px solid {c.get('accent', '#444')}40;">
          <div class="kde-titlebar" style="background: {c['bg']}; border-bottom: 1px solid {c.get('accent', '#444')}30;">
            <span style="color: {c['fg']};">System Settings</span>
            <div class="kde-buttons">
              <span class="kde-btn" style="background: {c['yellow']};"></span>
              <span class="kde-btn" style="background: {c['green']};"></span>
              <span class="kde-btn" style="background: {c['red']};"></span>
            </div>
          </div>
          <div style="padding: 12px;">
            <div style="color: {c['fg']}; margin-bottom: 8px;">Appearance</div>
            <div class="kde-list-item selected" style="background: {c['accent']}; color: {c['bg']}; padding: 6px 10px; border-radius: 4px; margin-bottom: 4px;">Global Theme</div>
            <div class="kde-list-item" style="color: {c['fg']}; padding: 6px 10px; margin-bottom: 4px;">Colors</div>
            <div class="kde-list-item" style="color: {c['fg_dim']}; padding: 6px 10px;">Icons</div>
          </div>
        </div>
      </div>

      <!-- Palette -->
      <div class="palette">
        <div class="swatch" style="background: {c['bg']};" title="bg"></div>
        <div class="swatch" style="background: {c['bg_alt']};" title="bg_alt"></div>
        <div class="swatch" style="background: {c['fg']};" title="fg"></div>
        <div class="swatch" style="background: {c['accent']};" title="accent"></div>
        <div class="swatch" style="background: {c.get('accent2', c['accent'])};" title="accent2"></div>
        <div class="swatch" style="background: {c['red']};" title="red"></div>
        <div class="swatch" style="background: {c['green']};" title="green"></div>
        <div class="swatch" style="background: {c['yellow']};" title="yellow"></div>
        <div class="swatch" style="background: {c['blue']};" title="blue"></div>
      </div>
      <div class="hex-row" style="color: {c['fg_dim']};">
        <span>{c['bg']}</span>
        <span>{c['bg_alt']}</span>
        <span>{c['fg']}</span>
        <span>{c['accent']}</span>
        <span>{c.get('accent2', '')}</span>
        <span>{c['red']}</span>
        <span>{c['green']}</span>
        <span>{c['yellow']}</span>
        <span>{c['blue']}</span>
      </div>
    </div>
    """


def generate_html(rices: list[dict], kde: dict | None) -> str:
    cards = ""
    for rice in rices:
        cards += render_rice_card(rice)
    if kde:
        cards += render_kde_card(kde)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Linta — Theme Preview</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'JetBrains Mono', monospace;
    background: #0a0a12;
    color: #ccc;
    padding: 40px 20px;
  }}

  h1 {{
    text-align: center;
    color: #fff;
    font-size: 28px;
    margin-bottom: 8px;
  }}

  .subtitle {{
    text-align: center;
    color: #666;
    font-size: 13px;
    margin-bottom: 40px;
  }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(520px, 1fr));
    gap: 32px;
    max-width: 1200px;
    margin: 0 auto;
  }}

  .theme-card {{
    border-radius: 12px;
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
  }}

  .bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 12px;
    font-size: 13px;
    margin-bottom: 2px;
    border-radius: 4px 4px 0 0;
  }}

  .bar-left, .bar-right {{ display: flex; align-items: center; gap: 4px; }}
  .ws {{ padding: 2px 6px; }}
  .ws.active {{ padding-bottom: 0; }}

  .desktop {{
    position: relative;
    min-height: 240px;
    border-radius: 0 0 4px 4px;
    padding: 12px;
    margin-bottom: 12px;
  }}

  .terminal {{
    width: 70%;
    border-radius: 8px;
    overflow: hidden;
  }}

  .term-titlebar {{
    padding: 4px 10px;
    font-size: 11px;
  }}

  .term-content {{
    padding: 10px 12px;
    font-size: 12px;
    line-height: 1.6;
  }}

  .notification {{
    position: absolute;
    top: 12px;
    right: 12px;
    width: 200px;
    padding: 10px 14px;
  }}

  .launcher {{
    position: absolute;
    bottom: 12px;
    right: 12px;
    width: 220px;
  }}

  .launcher-input {{
    padding: 8px 12px;
    font-size: 13px;
  }}

  .launcher-item {{
    padding: 6px 12px;
    font-size: 12px;
  }}

  .launcher-item.selected {{
    border-radius: 0 0 6px 6px;
  }}

  .lockscreen {{
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 12px;
  }}

  .lock-ring {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  .lock-inner {{
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: bold;
  }}

  .palette {{
    display: flex;
    gap: 4px;
    margin-top: 8px;
  }}

  .swatch {{
    flex: 1;
    height: 28px;
    border-radius: 4px;
    cursor: pointer;
    transition: transform 0.15s;
  }}

  .swatch:hover {{
    transform: scaleY(1.5);
  }}

  .hex-row {{
    display: flex;
    gap: 4px;
    margin-top: 4px;
    font-size: 9px;
  }}

  .hex-row span {{
    flex: 1;
    text-align: center;
  }}

  .kde-window {{
    width: 75%;
    border-radius: 8px;
    overflow: hidden;
  }}

  .kde-titlebar {{
    padding: 8px 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .kde-buttons {{
    display: flex;
    gap: 6px;
  }}

  .kde-btn {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
  }}
</style>
</head>
<body>
  <h1>Linta — Theme Preview</h1>
  <p class="subtitle">Hover over color swatches to see hex values. These are mockups of how each theme looks in context.</p>
  <div class="grid">
    {cards}
  </div>
</body>
</html>"""


def main() -> None:
    rices = []
    for rice_dir in sorted(NIRI_DIR.iterdir()):
        if rice_dir.is_dir() and rice_dir.name.startswith("rice-"):
            data = load_rice(rice_dir)
            if data:
                rices.append(data)

    kde = load_rice(KDE_DIR)

    html = generate_html(rices, kde)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html)
    print(f"Preview generated: {OUTPUT}")

    if "--no-open" not in sys.argv:
        webbrowser.open(f"file://{OUTPUT}")
        print("Opened in browser.")


if __name__ == "__main__":
    main()
