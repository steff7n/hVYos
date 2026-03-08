const PRESETS = {
  "Dusk": {
    name: "Dusk", description: "Warm dark theme — deep navy with amber accents",
    colors: {
      bg: "#1a1b2e", bg_alt: "#232440", fg: "#c8c8d0", fg_dim: "#6e6e82",
      accent: "#e0a526", accent2: "#9580ff",
      red: "#ff5555", green: "#50fa7b", yellow: "#f1fa8c", blue: "#6272a4",
      border_active: "#e0a526", border_inactive: "#2a2b45"
    },
    layout: { gaps: 8, outerGaps: 8, borderWidth: 2, borderRadius: 0 },
    waybar: { height: 34, position: "top", opacity: 0.92, fontSize: 13, borderWidth: 2 },
    mako: { borderRadius: 8, borderWidth: 2, opacity: 1.0, width: 350, position: "top-right" },
    fuzzel: { borderRadius: 8, borderWidth: 2, bgOpacity: 0.87 }
  },

  "Frost": {
    name: "Frost", description: "Cool dark theme — midnight with ice blue accents",
    colors: {
      bg: "#0d1117", bg_alt: "#161b22", fg: "#e6edf3", fg_dim: "#8b949e",
      accent: "#58a6ff", accent2: "#39d353",
      red: "#f85149", green: "#39d353", yellow: "#e3b341", blue: "#58a6ff",
      border_active: "#58a6ff", border_inactive: "#21262d"
    },
    layout: { gaps: 8, outerGaps: 8, borderWidth: 2, borderRadius: 0 },
    waybar: { height: 34, position: "top", opacity: 0.92, fontSize: 13, borderWidth: 2 },
    mako: { borderRadius: 8, borderWidth: 2, opacity: 1.0, width: 350, position: "top-right" },
    fuzzel: { borderRadius: 8, borderWidth: 2, bgOpacity: 0.87 }
  },

  "Forest": {
    name: "Forest", description: "Green-tinted dark theme — earthy tones with emerald accents",
    colors: {
      bg: "#1a2118", bg_alt: "#243022", fg: "#d4cfbe", fg_dim: "#7a7a6e",
      accent: "#73c936", accent2: "#87a96b",
      red: "#e55b3a", green: "#73c936", yellow: "#d4a017", blue: "#5e8d87",
      border_active: "#73c936", border_inactive: "#2a3828"
    },
    layout: { gaps: 8, outerGaps: 8, borderWidth: 2, borderRadius: 0 },
    waybar: { height: 34, position: "top", opacity: 0.92, fontSize: 13, borderWidth: 2 },
    mako: { borderRadius: 8, borderWidth: 2, opacity: 1.0, width: 350, position: "top-right" },
    fuzzel: { borderRadius: 8, borderWidth: 2, bgOpacity: 0.87 }
  },

  "Ember": {
    name: "Ember", description: "High-contrast dark theme — charcoal with burnt orange accents",
    colors: {
      bg: "#181818", bg_alt: "#242424", fg: "#f0f0f0", fg_dim: "#808080",
      accent: "#ff6600", accent2: "#cc3333",
      red: "#cc3333", green: "#98c379", yellow: "#e5c07b", blue: "#4a7a96",
      border_active: "#ff6600", border_inactive: "#333333"
    },
    layout: { gaps: 8, outerGaps: 8, borderWidth: 2, borderRadius: 0 },
    waybar: { height: 34, position: "top", opacity: 0.92, fontSize: 13, borderWidth: 2 },
    mako: { borderRadius: 8, borderWidth: 2, opacity: 1.0, width: 350, position: "top-right" },
    fuzzel: { borderRadius: 8, borderWidth: 2, bgOpacity: 0.87 }
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
  }
};
