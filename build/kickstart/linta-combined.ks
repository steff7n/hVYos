# Linta Linux — Combined Profile Kickstart
# KDE Plasma + Niri, switchable at login via SDDM.
#
# Profile: [Combined]
# Spec reference: README.md §5.2
# Estimated ISO size: ~2.5–3.0 GB

%include linta-base.ks

# =====================================================================
# Graphical base packages
# =====================================================================
%packages --instLangs=en

# Screenshot
flameshot

# Clipboard (Wayland)
wl-clipboard
cliphist

# Audio stack (§3.6)
pipewire
pipewire-pulseaudio
pipewire-alsa
wireplumber

# Power management
power-profiles-daemon

# GPU
mesa-dri-drivers
mesa-vulkan-drivers

# Flatpak (§2.3)
flatpak

# Fonts
dejavu-sans-fonts
dejavu-sans-mono-fonts
google-noto-emoji-fonts

# =====================================================================
# KDE Plasma packages (from kde.ks)
# =====================================================================

# Display manager
sddm

# Plasma desktop
plasma-desktop
plasma-workspace
kwin-wayland

# Xwayland — available per-session (used in KDE session, not in Niri)
xorg-x11-server-Xwayland

# KDE integration
systemsettings
powerdevil
plasma-nm
plasma-pa
kde-gtk-config
breeze-gtk
kscreenlocker
breeze-icon-theme
plasma-integration
kvantum
kscreen
plasma-systemmonitor
qt6-qtwayland

# =====================================================================
# Niri packages (from niri.ks)
# =====================================================================

# niri — custom RPM needed
# TODO: build linta-niri RPM

# Niri ecosystem
fuzzel
foot
waybar
mako
swaylock
qt5-qtwayland
polkit-gnome
xdg-desktop-portal
xdg-desktop-portal-gtk
xdg-desktop-portal-wlr

%end

# =====================================================================
# Combined-specific post-install
# =====================================================================
%post --erroronfail

# Set profile variant
sed -i 's|VARIANT_ID=PROFILE_PLACEHOLDER|VARIANT_ID=combined|' /etc/linta-release

# Boot to graphical target
systemctl set-default graphical.target

# Enable SDDM
systemctl enable sddm.service

# PipeWire user units
mkdir -p /etc/skel/.config/systemd/user/default.target.wants
ln -sf /usr/lib/systemd/user/pipewire.socket /etc/skel/.config/systemd/user/default.target.wants/pipewire.socket
ln -sf /usr/lib/systemd/user/wireplumber.service /etc/skel/.config/systemd/user/default.target.wants/wireplumber.service

# Flatpak + Flathub
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# SDDM Wayland config — use KWin as SDDM greeter compositor (works for both sessions)
mkdir -p /etc/sddm.conf.d
cat > /etc/sddm.conf.d/10-wayland.conf <<'SDDM'
[General]
DisplayServer=wayland
GreeterEnvironment=QT_WAYLAND_SHELL_INTEGRATION=layer-shell

[Wayland]
CompositorCommand=kwin_wayland --drm --no-lockscreen --no-global-shortcuts --locale1
SDDM

# Default to KDE Plasma session (user can switch to Niri at login screen)
mkdir -p /var/lib/sddm
echo '[Last]' > /var/lib/sddm/state.conf
echo 'Session=/usr/share/wayland-sessions/plasma.desktop' >> /var/lib/sddm/state.conf

# Create Niri session entry (same as niri.ks)
mkdir -p /usr/share/wayland-sessions
cat > /usr/share/wayland-sessions/niri.desktop <<'DESKTOP'
[Desktop Entry]
Name=Niri
Comment=Scrollable tiling Wayland compositor
Exec=niri-session
Type=Application
DesktopNames=niri
DESKTOP

cat > /usr/local/bin/niri-session <<'SESSION'
#!/bin/bash
export XDG_SESSION_TYPE=wayland
export XDG_CURRENT_DESKTOP=niri
export MOZ_ENABLE_WAYLAND=1
export QT_QPA_PLATFORM=wayland
export SDL_VIDEODRIVER=wayland
export CLUTTER_BACKEND=wayland
export GDK_BACKEND=wayland

/usr/libexec/polkit-gnome-authentication-agent-1 &
mako &
exec niri
SESSION
chmod +x /usr/local/bin/niri-session

# Default Niri config for Combined profile users who switch to Niri
mkdir -p /etc/skel/.config/niri
cat > /etc/skel/.config/niri/config.kdl <<'NIRI'
input {
    keyboard {
        xkb {
            layout "us"
        }
    }
    touchpad {
        tap
        natural-scroll
    }
}

layout {
    gaps 8
    center-focused-column "never"

    preset-column-widths {
        proportion 0.33333
        proportion 0.5
        proportion 0.66667
    }

    default-column-width { proportion 0.5; }

    focus-ring {
        width 2
        active-color "#7fc8ff"
        inactive-color "#505050"
    }

    border {
        off
    }
}

spawn-at-startup "waybar"

screenshot-path "~/Pictures/Screenshots/Screenshot-%Y-%m-%d-%H-%M-%S.png"

binds {
    Mod+Return { spawn "foot"; }
    Mod+D { spawn "fuzzel"; }
    Mod+Q { close-window; }
    Mod+Shift+E { quit; }
    Mod+Shift+Slash { show-hotkey-overlay; }

    Mod+Left { focus-column-left; }
    Mod+Right { focus-column-right; }
    Mod+Up { focus-window-up; }
    Mod+Down { focus-window-down; }

    Mod+Shift+Left { move-column-left; }
    Mod+Shift+Right { move-column-right; }
    Mod+Shift+Up { move-window-up; }
    Mod+Shift+Down { move-window-down; }

    Mod+Home { focus-column-first; }
    Mod+End { focus-column-last; }

    Mod+R { switch-preset-column-width; }
    Mod+F { maximize-column; }
    Mod+Shift+F { fullscreen-window; }
    Mod+C { center-column; }

    Mod+Minus { set-column-width "-10%"; }
    Mod+Equal { set-column-width "+10%"; }
    Mod+Shift+Minus { set-window-height "-10%"; }
    Mod+Shift+Equal { set-window-height "+10%"; }

    Mod+1 { focus-workspace 1; }
    Mod+2 { focus-workspace 2; }
    Mod+3 { focus-workspace 3; }
    Mod+4 { focus-workspace 4; }
    Mod+5 { focus-workspace 5; }

    Mod+Shift+1 { move-column-to-workspace 1; }
    Mod+Shift+2 { move-column-to-workspace 2; }
    Mod+Shift+3 { move-column-to-workspace 3; }
    Mod+Shift+4 { move-column-to-workspace 4; }
    Mod+Shift+5 { move-column-to-workspace 5; }

    Mod+Comma { consume-window-into-column; }
    Mod+Period { expel-window-from-column; }

    Mod+L { spawn "swaylock" "-f"; }

    Print { screenshot; }
    Ctrl+Print { screenshot-screen; }
    Alt+Print { screenshot-window; }

    XF86AudioRaiseVolume { spawn "wpctl" "set-volume" "@DEFAULT_AUDIO_SINK@" "5%+"; }
    XF86AudioLowerVolume { spawn "wpctl" "set-volume" "@DEFAULT_AUDIO_SINK@" "5%-"; }
    XF86AudioMute { spawn "wpctl" "set-mute" "@DEFAULT_AUDIO_SINK@" "toggle"; }
}
NIRI

%end
