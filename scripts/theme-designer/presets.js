const PRESETS = {
  "Dusk": {
    name: "Dusk", description: "Floating lounge — warm windows hovering in amber-lit darkness",
    colors: {
      bg: "#1c1826", bg_alt: "#27223a", fg: "#ccc5d0", fg_dim: "#6a6478",
      accent: "#d4a04e", accent2: "#8b6cc0",
      red: "#e05252", green: "#50d880", yellow: "#e8d07a", blue: "#6878a8",
      border_active: "#d4a04e", border_inactive: "#302840"
    },
    layout: { gaps: 6, outerGaps: 14, borderWidth: 1, borderRadius: 6 },
    waybar: { height: 28, position: "bottom", opacity: 0.78, fontSize: 12, borderWidth: 0 },
    mako: { borderRadius: 12, borderWidth: 0, opacity: 0.85, width: 320, position: "bottom-right" },
    fuzzel: { borderRadius: 12, borderWidth: 1, bgOpacity: 0.80 },
    modules: {
      left: ["workspaces"],
      center: ["clock"],
      right: ["volume", "network", "tray"]
    }
  },

  "Frost": {
    name: "Frost", description: "Cryo lab — clinical precision, tight geometry, arctic palette",
    colors: {
      bg: "#080e16", bg_alt: "#101a24", fg: "#dce6f0", fg_dim: "#4a5c6e",
      accent: "#7ec8e3", accent2: "#44b89d",
      red: "#e8504a", green: "#44b89d", yellow: "#d4b84a", blue: "#5a8cba",
      border_active: "#7ec8e3", border_inactive: "#162028"
    },
    layout: { gaps: 2, outerGaps: 4, borderWidth: 1, borderRadius: 0 },
    waybar: { height: 26, position: "top", opacity: 1.0, fontSize: 11, borderWidth: 0 },
    mako: { borderRadius: 0, borderWidth: 1, opacity: 0.92, width: 260, position: "top-left" },
    fuzzel: { borderRadius: 0, borderWidth: 1, bgOpacity: 0.94 },
    modules: {
      left: ["workspaces"],
      center: ["clock"],
      right: ["cpu", "memory", "network", "tray"]
    }
  },

  "Forest": {
    name: "Forest", description: "Canopy — organic spaciousness, rounded borderless windows in deep green",
    colors: {
      bg: "#111c10", bg_alt: "#1c2e1a", fg: "#ccc8b8", fg_dim: "#6a7060",
      accent: "#5fad30", accent2: "#7a9960",
      red: "#d85535", green: "#5fad30", yellow: "#c89a20", blue: "#4a8a7a",
      border_active: "#5fad30", border_inactive: "#1e3018"
    },
    layout: { gaps: 12, outerGaps: 16, borderWidth: 0, borderRadius: 14 },
    waybar: { height: 40, position: "top", opacity: 0.65, fontSize: 15, borderWidth: 0 },
    mako: { borderRadius: 16, borderWidth: 0, opacity: 0.78, width: 400, position: "top-left" },
    fuzzel: { borderRadius: 16, borderWidth: 0, bgOpacity: 0.72 },
    modules: {
      left: ["workspaces", "window"],
      center: ["clock"],
      right: ["volume", "network", "battery", "tray"]
    }
  },

  "Ember": {
    name: "Ember", description: "Foundry — dense industrial grid, thick borders, volcanic palette",
    colors: {
      bg: "#140c08", bg_alt: "#201410", fg: "#ece4dc", fg_dim: "#786858",
      accent: "#e85d26", accent2: "#b83030",
      red: "#b83030", green: "#8ab860", yellow: "#d4aa50", blue: "#4a7a96",
      border_active: "#e85d26", border_inactive: "#2c1c14"
    },
    layout: { gaps: 3, outerGaps: 0, borderWidth: 4, borderRadius: 0 },
    waybar: { height: 30, position: "bottom", opacity: 1.0, fontSize: 12, borderWidth: 3 },
    mako: { borderRadius: 0, borderWidth: 3, opacity: 1.0, width: 300, position: "bottom-left" },
    fuzzel: { borderRadius: 0, borderWidth: 3, bgOpacity: 0.96 },
    modules: {
      left: ["workspaces"],
      center: ["clock"],
      right: ["cpu", "memory", "volume", "tray"]
    }
  },

  "Nord": {
    name: "Nord", description: "Arctic, north-bluish palette by Arctic Ice Studio",
    colors: {
      bg: "#2e3440", bg_alt: "#3b4252", fg: "#eceff4", fg_dim: "#4c566a",
      accent: "#88c0d0", accent2: "#81a1c1",
      red: "#bf616a", green: "#a3be8c", yellow: "#ebcb8b", blue: "#5e81ac",
      border_active: "#88c0d0", border_inactive: "#434c5e"
    },
    layout: { gaps: 10, outerGaps: 10, borderWidth: 2, borderRadius: 0 },
    waybar: { height: 34, position: "top", opacity: 0.90, fontSize: 13, borderWidth: 2 },
    mako: { borderRadius: 8, borderWidth: 2, opacity: 1.0, width: 350, position: "top-right" },
    fuzzel: { borderRadius: 8, borderWidth: 2, bgOpacity: 0.87 }
  },

  "Catppuccin Mocha": {
    name: "Catppuccin Mocha", description: "Soothing pastel theme by Catppuccin",
    colors: {
      bg: "#1e1e2e", bg_alt: "#313244", fg: "#cdd6f4", fg_dim: "#6c7086",
      accent: "#cba6f7", accent2: "#f5c2e7",
      red: "#f38ba8", green: "#a6e3a1", yellow: "#f9e2af", blue: "#89b4fa",
      border_active: "#cba6f7", border_inactive: "#45475a"
    },
    layout: { gaps: 8, outerGaps: 8, borderWidth: 2, borderRadius: 4 },
    waybar: { height: 36, position: "top", opacity: 0.88, fontSize: 13, borderWidth: 2 },
    mako: { borderRadius: 10, borderWidth: 2, opacity: 1.0, width: 350, position: "top-right" },
    fuzzel: { borderRadius: 10, borderWidth: 2, bgOpacity: 0.85 }
  },

  "Dracula": {
    name: "Dracula", description: "Dark theme with vibrant colors by Zeno Rocha",
    colors: {
      bg: "#282a36", bg_alt: "#44475a", fg: "#f8f8f2", fg_dim: "#6272a4",
      accent: "#bd93f9", accent2: "#ff79c6",
      red: "#ff5555", green: "#50fa7b", yellow: "#f1fa8c", blue: "#8be9fd",
      border_active: "#bd93f9", border_inactive: "#44475a"
    },
    layout: { gaps: 8, outerGaps: 8, borderWidth: 2, borderRadius: 0 },
    waybar: { height: 34, position: "top", opacity: 0.92, fontSize: 13, borderWidth: 2 },
    mako: { borderRadius: 8, borderWidth: 2, opacity: 1.0, width: 350, position: "top-right" },
    fuzzel: { borderRadius: 8, borderWidth: 2, bgOpacity: 0.87 }
  },

  "Gruvbox Dark": {
    name: "Gruvbox Dark", description: "Retro groove color scheme by morhetz",
    colors: {
      bg: "#282828", bg_alt: "#3c3836", fg: "#ebdbb2", fg_dim: "#928374",
      accent: "#fabd2f", accent2: "#fe8019",
      red: "#fb4934", green: "#b8bb26", yellow: "#fabd2f", blue: "#83a598",
      border_active: "#fabd2f", border_inactive: "#504945"
    },
    layout: { gaps: 6, outerGaps: 6, borderWidth: 3, borderRadius: 0 },
    waybar: { height: 34, position: "top", opacity: 0.94, fontSize: 13, borderWidth: 2 },
    mako: { borderRadius: 4, borderWidth: 2, opacity: 1.0, width: 350, position: "top-right" },
    fuzzel: { borderRadius: 4, borderWidth: 2, bgOpacity: 0.90 }
  },

  "Tokyo Night": {
    name: "Tokyo Night", description: "Clean dark theme inspired by Tokyo city lights",
    colors: {
      bg: "#1a1b26", bg_alt: "#24283b", fg: "#c0caf5", fg_dim: "#565f89",
      accent: "#7aa2f7", accent2: "#bb9af7",
      red: "#f7768e", green: "#9ece6a", yellow: "#e0af68", blue: "#7dcfff",
      border_active: "#7aa2f7", border_inactive: "#292e42"
    },
    layout: { gaps: 8, outerGaps: 8, borderWidth: 2, borderRadius: 2 },
    waybar: { height: 34, position: "top", opacity: 0.90, fontSize: 13, borderWidth: 2 },
    mako: { borderRadius: 8, borderWidth: 2, opacity: 1.0, width: 350, position: "top-right" },
    fuzzel: { borderRadius: 8, borderWidth: 2, bgOpacity: 0.86 }
  },

  // ── Techno Layouts ──────────────────────────────────────────────

  "Pulse": {
    name: "Pulse",
    description: "Surgical precision — zero outer gaps, hairline borders, bottom bar, stripped modules",
    colors: {
      bg: "#07080a", bg_alt: "#101218", fg: "#b0b8c8", fg_dim: "#3c4354",
      accent: "#00e0f0", accent2: "#b44dff",
      red: "#ff3b5c", green: "#00e676", yellow: "#ffca28", blue: "#448aff",
      border_active: "#00e0f0", border_inactive: "#1a1d27"
    },
    layout: { gaps: 2, outerGaps: 0, borderWidth: 1, borderRadius: 0 },
    waybar: { height: 26, position: "bottom", opacity: 1.0, fontSize: 11, borderWidth: 1 },
    mako: { borderRadius: 0, borderWidth: 1, opacity: 0.95, width: 280, position: "top-right" },
    fuzzel: { borderRadius: 0, borderWidth: 1, bgOpacity: 0.95 },
    modules: {
      left: ["workspaces"],
      center: ["clock"],
      right: ["volume", "network", "tray"]
    }
  },

  "Grid": {
    name: "Grid",
    description: "Brutalist geometry — zero gaps, thick grid-line borders, monochrome, minimal",
    colors: {
      bg: "#000000", bg_alt: "#0a0a0a", fg: "#d4d4d4", fg_dim: "#525252",
      accent: "#ffffff", accent2: "#a3a3a3",
      red: "#ff2d2d", green: "#00cc44", yellow: "#ffcc00", blue: "#0088ff",
      border_active: "#ffffff", border_inactive: "#333333"
    },
    layout: { gaps: 0, outerGaps: 0, borderWidth: 4, borderRadius: 0 },
    waybar: { height: 24, position: "bottom", opacity: 1.0, fontSize: 11, borderWidth: 0 },
    mako: { borderRadius: 0, borderWidth: 3, opacity: 1.0, width: 260, position: "bottom-left" },
    fuzzel: { borderRadius: 0, borderWidth: 3, bgOpacity: 0.98 },
    modules: {
      left: ["workspaces"],
      center: ["clock"],
      right: ["cpu", "memory", "tray"]
    }
  },

  "Signal": {
    name: "Signal",
    description: "Ambient operator — borderless floating windows, translucent bar, HUD readout",
    colors: {
      bg: "#0a0e14", bg_alt: "#111a22", fg: "#8faabb", fg_dim: "#3d5566",
      accent: "#2ee6a8", accent2: "#0098db",
      red: "#f05050", green: "#2ee6a8", yellow: "#e6c84e", blue: "#3daee9",
      border_active: "#2ee6a8", border_inactive: "#152028"
    },
    layout: { gaps: 6, outerGaps: 6, borderWidth: 0, borderRadius: 0 },
    waybar: { height: 28, position: "bottom", opacity: 0.75, fontSize: 12, borderWidth: 0 },
    mako: { borderRadius: 0, borderWidth: 0, opacity: 0.88, width: 320, position: "top-left" },
    fuzzel: { borderRadius: 0, borderWidth: 0, bgOpacity: 0.82 },
    modules: {
      left: ["workspaces", "window"],
      center: ["clock"],
      right: ["cpu", "memory", "network", "tray"]
    }
  }
};
