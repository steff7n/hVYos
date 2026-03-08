# Linta Linux — Bare Profile Kickstart
# TTY-only. No display manager, no compositor, no GUI apps.
#
# Profile: [Bare]
# Spec reference: README.md §5.2
# Estimated ISO size: ~1.0–1.2 GB

%include linta-base.ks

# =====================================================================
# Bare profile — no additional packages beyond base
# =====================================================================
%packages --instLangs=en

# Explicitly exclude graphical components
-sddm
-plasma-desktop
-plasma-workspace
-xorg-x11-server-Xwayland
-wl-clipboard
-flameshot
-pipewire
-pipewire-pulseaudio
-pipewire-alsa
-wireplumber
-flatpak
-power-profiles-daemon
-mesa-dri-drivers

%end

# =====================================================================
# Bare-specific post-install
# =====================================================================
%post --erroronfail

# Set profile variant in release info
sed -i 's|VARIANT_ID=PROFILE_PLACEHOLDER|VARIANT_ID=bare|' /etc/linta-release

# No display manager — boot to TTY
systemctl set-default multi-user.target

# Configure console font for readability
echo 'FONT=eurlatgr' > /etc/vconsole.conf

%end
