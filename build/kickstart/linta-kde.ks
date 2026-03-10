# Linta Linux — KDE Plasma Profile Kickstart
# Full KDE Plasma desktop on Wayland with Xwayland compatibility.
#
# Profile: [KDE]
# Spec reference: README.md §5.2, §8.3
# Estimated ISO size: ~2.0–2.5 GB

%include linta-base.ks

# =====================================================================
# Graphical base packages (shared with Niri/Combined)
# Spec: README.md §8.2 (graphical subset)
# =====================================================================
%packages --instLangs=en

# Screenshot
flameshot

# Clipboard (Wayland)
wl-clipboard

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

# Fonts (minimal — font wizard handles the rest)
dejavu-sans-fonts
dejavu-sans-mono-fonts
google-noto-emoji-fonts

# =====================================================================
# KDE Plasma packages
# Spec: README.md §5.2, §8.3
# =====================================================================

# Display manager (§5.3)
sddm

# Plasma desktop
plasma-desktop
plasma-workspace
kwin-wayland

# Xwayland compatibility (§5.1)
xorg-x11-server-Xwayland

# KDE system integration
plasma-systemsettings
powerdevil
plasma-nm
plasma-pa
kde-gtk-config
breeze-gtk

# Session lock (§5.4)
kscreenlocker

# Theming
breeze-icon-theme
plasma-integration
kvantum

# KDE utilities for base functionality
kscreen
plasma-systemmonitor

# Qt Wayland
qt6-qtwayland

%end

# =====================================================================
# KDE-specific post-install
# =====================================================================
%post --erroronfail

# Set profile variant
sed -i 's|VARIANT_ID=PROFILE_PLACEHOLDER|VARIANT_ID=kde|' /etc/linta-release

# Boot to graphical target
systemctl set-default graphical.target

# Enable SDDM (§5.3)
systemctl enable sddm.service

# Enable PipeWire for all users via systemd user units
mkdir -p /etc/skel/.config/systemd/user/default.target.wants
ln -sf /usr/lib/systemd/user/pipewire.socket /etc/skel/.config/systemd/user/default.target.wants/pipewire.socket
ln -sf /usr/lib/systemd/user/wireplumber.service /etc/skel/.config/systemd/user/default.target.wants/wireplumber.service

# The linta user was created before %post, so /etc/skel changes don't apply to it
mkdir -p /home/linta/.config/systemd/user/default.target.wants
ln -sf /usr/lib/systemd/user/pipewire.socket /home/linta/.config/systemd/user/default.target.wants/pipewire.socket
ln -sf /usr/lib/systemd/user/wireplumber.service /home/linta/.config/systemd/user/default.target.wants/wireplumber.service
chown -R linta:linta /home/linta/.config

# Configure Flatpak with Flathub (§2.3)
# Non-fatal: network may not be available inside the build chroot
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo || true

# Force Wayland session as default for SDDM
mkdir -p /etc/sddm.conf.d
cat > /etc/sddm.conf.d/10-wayland.conf <<'SDDM'
[General]
DisplayServer=wayland
GreeterEnvironment=QT_WAYLAND_SHELL_INTEGRATION=layer-shell

[Wayland]
CompositorCommand=kwin_wayland --drm --no-lockscreen --no-global-shortcuts --locale1
SDDM

# Set KDE Wayland as the default session
mkdir -p /var/lib/sddm
echo '[Last]' > /var/lib/sddm/state.conf
echo 'Session=/usr/share/wayland-sessions/plasma.desktop' >> /var/lib/sddm/state.conf

%end
