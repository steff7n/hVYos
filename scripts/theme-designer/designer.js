/* Linta Niri Theme Designer — core logic */

// ── State ──
const S = {
  colors: {},
  layout: {},
  waybar: {},
  mako: {},
  fuzzel: {},
  modules: {
    left: ["workspaces", "window"],
    center: ["clock"],
    right: ["volume", "network", "cpu", "memory", "battery", "tray"]
  }
};

const ALL_MODULES = ["workspaces", "window", "clock", "cpu", "memory", "battery", "network", "volume", "tray"];

const MODULE_RENDER = {
  workspaces: (c) => {
    const ws = [1,2,3,4,5];
    return ws.map((n,i) => {
      const active = i === 1;
      return `<span class="bar-ws" style="color:${active ? c.accent : c.fg_dim};${active ? 'border-bottom-color:'+c.accent : ''}">${n}</span>`;
    }).join('');
  },
  window:     (c) => `<span class="bar-module" style="color:${c.fg}">~/Projects/linta</span>`,
  clock:      (c) => `<span class="bar-module" style="color:${c.fg};font-weight:bold">${new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',hour12:false})}</span>`,
  cpu:        (c) => `<span class="bar-module" style="color:${c.fg}"> 23%</span>`,
  memory:     (c) => `<span class="bar-module" style="color:${c.fg}"> 45%</span>`,
  battery:    (c) => `<span class="bar-module" style="color:${c.fg}"> 92%</span>`,
  network:    (c) => `<span class="bar-module" style="color:${c.fg}"> 78%</span>`,
  volume:     (c) => `<span class="bar-module" style="color:${c.fg}"> 65%</span>`,
  tray:       (c) => `<span class="bar-module" style="color:${c.fg_dim}">◆</span>`,
};

// ── Helpers ──
function hexToRgba(hex, a) {
  const r = parseInt(hex.slice(1,3),16), g = parseInt(hex.slice(3,5),16), b = parseInt(hex.slice(5,7),16);
  return `rgba(${r},${g},${b},${a})`;
}

function deepSet(obj, path, val) {
  const keys = path.split('.');
  let cur = obj;
  for (let i = 0; i < keys.length - 1; i++) cur = cur[keys[i]];
  cur[keys[keys.length-1]] = val;
}

function deepGet(obj, path) {
  return path.split('.').reduce((o,k) => o[k], obj);
}

// ── Load preset into state ──
function loadPreset(name) {
  const p = PRESETS[name];
  if (!p) return;
  Object.assign(S.colors, JSON.parse(JSON.stringify(p.colors)));
  Object.assign(S.layout, JSON.parse(JSON.stringify(p.layout)));
  Object.assign(S.waybar, JSON.parse(JSON.stringify(p.waybar)));
  Object.assign(S.mako, JSON.parse(JSON.stringify(p.mako)));
  Object.assign(S.fuzzel, JSON.parse(JSON.stringify(p.fuzzel)));
  S.modules = p.modules
    ? JSON.parse(JSON.stringify(p.modules))
    : { left: ["workspaces","window"], center: ["clock"], right: ["volume","network","cpu","memory","battery","tray"] };
  document.getElementById('exportName').value = p.name.toLowerCase().replace(/\s+/g,'-');
  document.getElementById('exportDesc').value = p.description;
  syncControlsFromState();
  render();
}

// ── Sync controls to match state ──
function syncControlsFromState() {
  // Colors
  const ps = document.getElementById('paletteSection');
  ps.querySelectorAll('.color-row').forEach(r => r.remove());
  const colorKeys = Object.keys(S.colors);
  colorKeys.forEach(key => {
    const row = document.createElement('div');
    row.className = 'color-row';
    row.innerHTML = `<label>${key}</label><input type="color" value="${S.colors[key]}" data-color="${key}"><input type="text" class="color-hex" value="${S.colors[key]}" data-color-hex="${key}">`;
    ps.appendChild(row);
  });

  // Sliders
  document.querySelectorAll('input[type="range"][data-key]').forEach(sl => {
    const key = sl.dataset.key;
    let val = deepGet(S, key);
    if (key.includes('opacity') || key.includes('bgOpacity')) val = Math.round(val * 100);
    sl.value = val;
    sl.nextElementSibling.textContent = sl.value;
  });

  // Selects
  document.querySelectorAll('select[data-key]').forEach(sel => {
    sel.value = deepGet(S, sel.dataset.key);
  });

  // Module checkboxes
  rebuildModuleChecks();
}

function rebuildModuleChecks() {
  ['left','center','right'].forEach(zone => {
    const container = document.getElementById('modules' + zone.charAt(0).toUpperCase() + zone.slice(1));
    container.innerHTML = '';
    ALL_MODULES.forEach(mod => {
      const lbl = document.createElement('label');
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.checked = S.modules[zone].includes(mod);
      cb.dataset.zone = zone;
      cb.dataset.mod = mod;
      cb.addEventListener('change', onModuleChange);
      lbl.appendChild(cb);
      lbl.appendChild(document.createTextNode(' ' + mod));
      container.appendChild(lbl);
    });
  });
}

// ── Render preview ──
function render() {
  const c = S.colors;
  const l = S.layout;
  const w = S.waybar;
  const m = S.mako;
  const f = S.fuzzel;

  // Desktop BG
  document.getElementById('desktopBg').style.background = c.bg;

  // Waybar
  const bar = document.getElementById('waybar');
  bar.style.height = w.height + 'px';
  bar.style.background = hexToRgba(c.bg, w.opacity);
  bar.style.fontSize = w.fontSize + 'px';
  bar.style.borderBottom = w.position === 'top' ? `${w.borderWidth}px solid ${c.accent}` : 'none';
  bar.style.borderTop = w.position === 'bottom' ? `${w.borderWidth}px solid ${c.accent}` : 'none';
  bar.className = 'preview-bar ' + w.position;

  // Bar modules
  ['left','center','right'].forEach(zone => {
    const el = document.getElementById('bar' + zone.charAt(0).toUpperCase() + zone.slice(1));
    el.innerHTML = S.modules[zone].map(mod => MODULE_RENDER[mod] ? MODULE_RENDER[mod](c) : '').join('');
  });

  // Windows
  const vp = document.getElementById('viewport');
  const vpW = vp.clientWidth;
  const vpH = vp.clientHeight;
  const barH = w.height + w.borderWidth;
  const og = l.outerGaps;
  const ig = l.gaps;
  const bw = l.borderWidth;
  const br = l.borderRadius;

  const area = document.getElementById('windowsArea');
  const areaTop = (w.position === 'top' ? barH : 0) + og;
  const areaLeft = og;
  const areaH = vpH - barH - og * 2;
  const availW = vpW - og * 2;
  area.style.top = areaTop + 'px';
  area.style.left = areaLeft + 'px';
  area.style.width = availW + 'px';
  area.style.height = areaH + 'px';
  area.style.gap = ig + 'px';

  const winW = Math.floor((availW - ig * 2) / 3);
  [['win1', true], ['win2', false], ['win3', false]].forEach(([id, active]) => {
    const win = document.getElementById(id);
    win.style.width = (id === 'win3' ? winW * 0.6 : winW) + 'px';
    win.style.height = areaH + 'px';
    win.style.border = `${bw}px solid ${active ? c.border_active : c.border_inactive}`;
    win.style.borderRadius = br + 'px';
    win.style.background = c.bg_alt;
    win.style.overflow = 'hidden';
  });

  // Window titlebars
  ['1','2','3'].forEach(n => {
    const tb = document.getElementById('win'+n+'Title');
    tb.style.background = c.bg;
    tb.style.color = c.fg;
    tb.style.borderBottom = `1px solid ${c.border_inactive}`;
    document.getElementById('dotY'+n).style.background = c.yellow;
    document.getElementById('dotG'+n).style.background = c.green;
    document.getElementById('dotR'+n).style.background = c.red;
  });

  // Win1 content: terminal
  document.getElementById('win1Content').innerHTML =
    `<span style="color:${c.accent}">&#x276f;</span> <span style="color:${c.fg}">lintactl info</span><br>` +
    `<span style="color:${c.fg_dim}">  Linta 25.1</span><br>` +
    `<span style="color:${c.fg_dim}">  Profile:    niri</span><br>` +
    `<span style="color:${c.fg_dim}">  Theme:      </span><span style="color:${c.accent}">${document.getElementById('exportName').value}</span><br>` +
    `<span style="color:${c.green}">  SELinux:    Enforcing</span><br><br>` +
    `<span style="color:${c.accent}">&#x276f;</span> <span style="color:${c.fg}">git status</span><br>` +
    `<span style="color:${c.green}">  modified:   src/main.rs</span><br>` +
    `<span style="color:${c.red}">  deleted:    old_config.toml</span><br>` +
    `<span style="color:${c.yellow}">  new file:   README.md</span><br><br>` +
    `<span style="color:${c.accent}">&#x276f;</span> <span style="color:${c.fg};opacity:0.5">_</span>`;

  // Win2 content: browser
  document.getElementById('win2Content').innerHTML =
    `<div style="background:${c.bg};padding:6px 10px;border-radius:4px;margin-bottom:8px;border:1px solid ${c.border_inactive}">` +
    `<span style="color:${c.fg_dim}">&#x1f512; </span><span style="color:${c.accent}">lintalinux.org</span><span style="color:${c.fg_dim}">/docs</span></div>` +
    `<div style="color:${c.fg};font-size:14px;font-weight:bold;margin-bottom:6px">Linta Linux</div>` +
    `<div style="color:${c.fg_dim};font-size:11px;line-height:1.5">A lean, rolling-release distribution for developers. Btrfs snapshots, ` +
    `Wayland-native, zero telemetry.<br><br>` +
    `<span style="color:${c.accent}">Get Started</span> &nbsp; <span style="color:${c.blue}">Documentation</span></div>`;

  // Win3 content: editor
  document.getElementById('win3Content').innerHTML =
    `<div style="color:${c.fg_dim};font-size:11px">` +
    `<span style="color:${c.blue}">layout</span> {<br>` +
    `&nbsp;&nbsp;<span style="color:${c.accent}">gaps</span> <span style="color:${c.yellow}">${l.gaps}</span><br>` +
    `&nbsp;&nbsp;<span style="color:${c.accent}">border</span> {<br>` +
    `&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:${c.green}">width</span> <span style="color:${c.yellow}">${l.borderWidth}</span><br>` +
    `&nbsp;&nbsp;}<br>` +
    `}</div>`;

  // Position toggle buttons above waybar when bar is at bottom
  const toggles = document.querySelector('.overlay-toggles');
  if (w.position === 'bottom') {
    toggles.style.bottom = (w.height + w.borderWidth + 12) + 'px';
  } else {
    toggles.style.bottom = '12px';
  }

  // Notification
  const notif = document.getElementById('notification');
  notif.style.background = hexToRgba(c.bg_alt, m.opacity);
  notif.style.border = `${m.borderWidth}px solid ${c.accent}`;
  notif.style.borderRadius = m.borderRadius + 'px';
  notif.style.width = m.width + 'px';
  const [nv, nh] = m.position.split('-');
  notif.style.top = nv === 'top' ? (barH + og + 8) + 'px' : 'auto';
  notif.style.bottom = nv === 'bottom' ? (og + 8) + 'px' : 'auto';
  notif.style.right = nh === 'right' ? (og + 8) + 'px' : 'auto';
  notif.style.left = nh === 'left' ? (og + 8) + 'px' : 'auto';
  notif.querySelector('.notif-title').style.color = c.accent;
  notif.querySelector('.notif-body').style.color = c.fg;
  notif.querySelector('.notif-sub').style.color = c.fg_dim;

  // Launcher
  const lb = document.getElementById('launcherBox');
  lb.style.background = hexToRgba(c.bg, f.bgOpacity);
  lb.style.border = `${f.borderWidth}px solid ${c.accent}`;
  lb.style.borderRadius = f.borderRadius + 'px';
  lb.style.overflow = 'hidden';
  document.getElementById('launcherOverlay').style.background = hexToRgba(c.bg, 0.5);
  document.getElementById('launcherInput').style.borderBottom = `1px solid ${c.border_inactive}`;
  document.getElementById('launcherInput').style.color = c.fg;
  document.getElementById('launcherPrompt').style.color = c.accent;
  document.getElementById('launcherSel').style.background = c.bg_alt;
  document.getElementById('launcherSel').style.color = c.accent;
  document.getElementById('launcherItem2').style.color = c.fg_dim;
  document.getElementById('launcherItem3').style.color = c.fg_dim;

  // Lock screen
  const lo = document.getElementById('lockOverlay');
  lo.style.background = c.bg;
  document.getElementById('lockRing').style.border = `6px solid ${c.accent}`;
  document.getElementById('lockInner').style.background = c.bg_alt;
  document.getElementById('lockInner').style.color = c.fg;
  document.getElementById('lockTime').textContent = new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',hour12:false});
  document.getElementById('lockText').style.color = c.fg_dim;
}

// ── Event wiring ──
function onColorChange(e) {
  const key = e.target.dataset.color || e.target.dataset.colorHex;
  if (!key) return;
  const val = e.target.value;
  if (!/^#[0-9a-fA-F]{6}$/.test(val)) return;
  S.colors[key] = val;
  const row = e.target.closest('.color-row');
  row.querySelector('input[type="color"]').value = val;
  row.querySelector('.color-hex').value = val;
  render();
}

function onSliderInput(e) {
  const key = e.target.dataset.key;
  let val = Number(e.target.value);
  if (key.includes('opacity') || key.includes('bgOpacity')) val = val / 100;
  deepSet(S, key, val);
  e.target.nextElementSibling.textContent = e.target.value;
  render();
}

function onSelectChange(e) {
  const key = e.target.dataset.key;
  deepSet(S, key, e.target.value);
  render();
}

function onModuleChange(e) {
  const { zone, mod } = e.target.dataset;
  if (e.target.checked) {
    if (!S.modules[zone].includes(mod)) S.modules[zone].push(mod);
  } else {
    S.modules[zone] = S.modules[zone].filter(m => m !== mod);
  }
  render();
}

// ── Export ──
function generateMetadata() {
  return JSON.stringify({
    name: document.getElementById('exportName').value,
    description: document.getElementById('exportDesc').value,
    profile: "niri",
    colors: S.colors
  }, null, 2);
}

function generateWaybarConfig() {
  const modMap = { workspaces: "niri/workspaces", window: "niri/window", clock: "clock",
    cpu: "cpu", memory: "memory", battery: "battery", network: "network", volume: "pulseaudio", tray: "tray" };
  const cfg = {
    layer: "top", position: S.waybar.position, height: S.waybar.height, spacing: 4,
    "modules-left": S.modules.left.map(m => modMap[m] || m),
    "modules-center": S.modules.center.map(m => modMap[m] || m),
    "modules-right": S.modules.right.map(m => modMap[m] || m),
    clock: { format: "{:%H:%M}", "format-alt": "{:%A, %B %d}", "tooltip-format": "{:%Y-%m-%d | %H:%M:%S}" },
    cpu: { format: "\uf4bc  {usage}%" },
    memory: { format: "\uf035b  {percentage}%" },
    battery: { format: "{icon}  {capacity}%", "format-icons": ["\uf244","\uf243","\uf242","\uf241","\uf240"] },
    network: { "format-wifi": "\uf1eb  {signalStrength}%", "format-ethernet": "\uf0ac  {ipaddr}", "format-disconnected": "\uf071  offline" },
    pulseaudio: { format: "{icon}  {volume}%", "format-muted": "\uf6a9  muted", "format-icons": { default: ["\uf026","\uf027","\uf028"] } },
    tray: { spacing: 8 }
  };
  return JSON.stringify(cfg, null, 2);
}

function generateWaybarCSS() {
  const c = S.colors, w = S.waybar;
  const bgRgba = hexToRgba(c.bg, w.opacity);
  const borderSide = w.position === 'top' ? 'border-bottom' : 'border-top';
  return `* {\n  font-family: "JetBrains Mono", "Symbols Nerd Font", monospace;\n  font-size: ${w.fontSize}px;\n  min-height: 0;\n}\n\n` +
    `window#waybar {\n  background: ${bgRgba};\n  color: ${c.fg};\n  ${borderSide}: ${w.borderWidth}px solid ${c.accent};\n}\n\n` +
    `#workspaces button {\n  padding: 0 8px;\n  color: ${c.fg_dim};\n  border: none;\n  border-radius: 0;\n  background: transparent;\n}\n\n` +
    `#workspaces button.active {\n  color: ${c.accent};\n  border-bottom: 2px solid ${c.accent};\n}\n\n` +
    `#clock {\n  color: ${c.fg};\n  font-weight: bold;\n}\n\n` +
    `#battery, #cpu, #memory, #network, #pulseaudio, #tray {\n  padding: 0 10px;\n  color: ${c.fg};\n}\n\n` +
    `#battery.warning { color: ${c.yellow}; }\n#battery.critical { color: ${c.red}; }\n#network.disconnected { color: ${c.fg_dim}; }\n`;
}

function generateMakoConfig() {
  const c = S.colors, m = S.mako;
  return `font=JetBrains Mono 11\nbackground-color=${c.bg_alt}\ntext-color=${c.fg}\nborder-color=${c.accent}\n` +
    `border-size=${m.borderWidth}\nborder-radius=${m.borderRadius}\ndefault-timeout=5000\npadding=12\nmargin=12\nwidth=${m.width}\n\n` +
    `[urgency=high]\nborder-color=${c.red}\ndefault-timeout=10000\n`;
}

function generateFuzzelIni() {
  const c = S.colors, f = S.fuzzel;
  const strip = h => h.replace('#','');
  const alphaHex = Math.round(f.bgOpacity * 255).toString(16).padStart(2,'0');
  return `[main]\nfont=JetBrains Mono:size=12\nprompt=\u276f \nterminal=foot\nlayer=overlay\n\n` +
    `[colors]\nbackground=${strip(c.bg)}${alphaHex}\ntext=${strip(c.fg)}ff\nselection=${strip(c.bg_alt)}ff\n` +
    `selection-text=${strip(c.accent)}ff\nmatch=${strip(c.accent)}ff\nborder=${strip(c.accent)}ff\n\n` +
    `[border]\nwidth=${f.borderWidth}\nradius=${f.borderRadius}\n`;
}

function generateSwaylockConfig() {
  const c = S.colors;
  return `color=${c.bg.replace('#','')}\ninside-color=${c.bg_alt.replace('#','')}\n` +
    `ring-color=${c.accent.replace('#','')}\nkey-hl-color=${c.accent2.replace('#','')}\n` +
    `line-color=00000000\nseparator-color=00000000\ntext-color=${c.fg.replace('#','')}\n` +
    `inside-ver-color=${c.bg_alt.replace('#','')}\nring-ver-color=${c.accent2.replace('#','')}\n` +
    `inside-wrong-color=${c.bg_alt.replace('#','')}\nring-wrong-color=${c.red.replace('#','')}\n` +
    `text-wrong-color=${c.red.replace('#','')}\ninside-clear-color=${c.bg_alt.replace('#','')}\n` +
    `ring-clear-color=${c.green.replace('#','')}\nindicator-radius=100\nindicator-thickness=10\n` +
    `font=JetBrains Mono\nfont-size=16\n`;
}

function generateNiriKdl() {
  const l = S.layout, c = S.colors;
  return `layout {\n    gaps ${l.gaps}\n\n    center-focused-column "never"\n\n` +
    `    preset-column-widths {\n        proportion 0.33333\n        proportion 0.5\n        proportion 0.66667\n    }\n\n` +
    `    default-column-width { proportion 0.5; }\n\n` +
    `    focus-ring {\n        width ${l.borderWidth}\n        active-color "${c.border_active}"\n        inactive-color "${c.border_inactive}"\n    }\n\n` +
    `    border {\n        off\n    }\n}\n`;
}

function generateApplySh() {
  return `#!/bin/bash\nset -euo pipefail\nRICE_DIR="$(cd "$(dirname "\${BASH_SOURCE[0]}")" && pwd)"\n` +
    `CONFIG_HOME="\${XDG_CONFIG_HOME:-$HOME/.config}"\n\n` +
    `mkdir -p "$CONFIG_HOME"/{waybar,mako,fuzzel,swaylock}\n` +
    `cp "$RICE_DIR/waybar/config.jsonc" "$CONFIG_HOME/waybar/config.jsonc"\n` +
    `cp "$RICE_DIR/waybar/style.css" "$CONFIG_HOME/waybar/style.css"\n` +
    `cp "$RICE_DIR/mako/config" "$CONFIG_HOME/mako/config"\n` +
    `cp "$RICE_DIR/fuzzel/fuzzel.ini" "$CONFIG_HOME/fuzzel/fuzzel.ini"\n` +
    `cp "$RICE_DIR/swaylock/config" "$CONFIG_HOME/swaylock/config"\n\n` +
    `pkill -SIGUSR2 waybar 2>/dev/null || true\nmakoctl reload 2>/dev/null || true\n\n` +
    `echo "Rice '${document.getElementById('exportName').value}' applied."\n`;
}

async function exportZip() {
  const zip = new JSZip();
  const name = document.getElementById('exportName').value || 'custom-rice';
  zip.file('metadata.json', generateMetadata());
  zip.file('waybar/config.jsonc', generateWaybarConfig());
  zip.file('waybar/style.css', generateWaybarCSS());
  zip.file('mako/config', generateMakoConfig());
  zip.file('fuzzel/fuzzel.ini', generateFuzzelIni());
  zip.file('swaylock/config', generateSwaylockConfig());
  zip.file('niri-snippet.kdl', generateNiriKdl());
  zip.file('apply.sh', generateApplySh());

  const blob = await zip.generateAsync({ type: 'blob' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `linta-rice-${name}.zip`;
  a.click();
  URL.revokeObjectURL(a.href);
}

function copyMetadata() {
  navigator.clipboard.writeText(generateMetadata()).then(() => {
    const btn = document.getElementById('btnCopyMeta');
    btn.textContent = 'Copied!';
    setTimeout(() => { btn.textContent = 'Copy metadata.json'; }, 1500);
  });
}

// ── Init ──
function init() {
  loadPreset('Dusk');

  document.getElementById('presetSelect').addEventListener('change', e => loadPreset(e.target.value));

  document.getElementById('paletteSection').addEventListener('input', e => {
    if (e.target.dataset.color || e.target.dataset.colorHex) onColorChange(e);
  });

  document.querySelectorAll('input[type="range"]').forEach(sl => sl.addEventListener('input', onSliderInput));
  document.querySelectorAll('select[data-key]').forEach(sel => sel.addEventListener('change', onSelectChange));

  document.getElementById('btnExport').addEventListener('click', exportZip);
  document.getElementById('btnCopyMeta').addEventListener('click', copyMetadata);

  document.getElementById('toggleLauncher').addEventListener('click', () => {
    const ol = document.getElementById('launcherOverlay');
    const btn = document.getElementById('toggleLauncher');
    ol.classList.toggle('visible');
    btn.classList.toggle('active');
    document.getElementById('lockOverlay').classList.remove('visible');
    document.getElementById('toggleLock').classList.remove('active');
  });

  document.getElementById('toggleLock').addEventListener('click', () => {
    const ol = document.getElementById('lockOverlay');
    const btn = document.getElementById('toggleLock');
    ol.classList.toggle('visible');
    btn.classList.toggle('active');
    document.getElementById('launcherOverlay').classList.remove('visible');
    document.getElementById('toggleLauncher').classList.remove('active');
    if (ol.classList.contains('visible')) render();
  });

  document.getElementById('exportName').addEventListener('input', render);

  window.addEventListener('resize', render);
  setInterval(() => {
    const clockEls = document.querySelectorAll('.bar-module');
    clockEls.forEach(el => {
      if (el.style.fontWeight === 'bold') {
        el.textContent = new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',hour12:false});
      }
    });
  }, 30000);
}

init();
