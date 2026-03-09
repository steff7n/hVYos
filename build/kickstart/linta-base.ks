# Linta Linux — Base Kickstart Configuration
# Shared by all profiles. Do NOT use this file directly —
# use a profile-specific .ks that %include's this.
#
# Profiles: [All]
# Spec reference: README.md §1–§4, §8.2, §11

# --- Installation source ---
# Fedora base repos — version is set at build time via ksflatten or sed
url --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-$releasever&arch=$basearch
repo --name=updates --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f$releasever&arch=$basearch

# --- Locale & Input ---
lang en_US.UTF-8
keyboard us
timezone UTC --utc

# --- Network ---
network --bootproto=dhcp --device=link --activate --onboot=on

# --- Security (§4) ---
selinux --enforcing
firewall --enabled --service=dhcpv6-client

# --- Auth ---
rootpw --lock
# Default user created by installer (Phase 8); for live/test ISO, create linta user
user --name=linta --groups=wheel --plaintext --password=linta

# --- Bootloader ---
bootloader --timeout=5 --append="rhgb quiet"

# --- Disk layout: Btrfs with @ and @home subvolumes (§3.1) ---
# zstd compression, CoW enabled
zerombr
clearpart --all --initlabel
part /boot/efi --fstype=efi --size=512
part /boot --fstype=ext4 --size=1024
part btrfs.01 --fstype=btrfs --size=1 --grow

btrfs none --label=linta --data=single btrfs.01
btrfs /     --subvol --name=@ btrfs.01
btrfs /home --subvol --name=@home btrfs.01

# --- Services ---
services --enabled=NetworkManager,firewalld,systemd-timesyncd,fstrim.timer

# --- Reboot after install ---
reboot

# =====================================================================
# Base packages — included in ALL profiles (including Bare)
# Spec: README.md §8.2
# =====================================================================
%packages --instLangs=en
@core
@standard

# Kernel
kernel
kernel-modules
kernel-modules-extra
linux-firmware

# Shell (§8.2)
zsh
zsh-syntax-highlighting
util-linux
util-linux-user

# Terminal editor
# helix — custom RPM needed, not in Fedora repos
# TODO: add when linta repo is available

# System monitor
btop

# Dev: C/C++ (§8.2)
gcc
gcc-c++
clang
make
cmake
gdb

# Dev: General
git
python3
openssh-clients

# Dev: Extended toolchain
clang-tools-extra
valgrind
strace
ltrace
autoconf
automake
pkgconf
meson
ninja-build
python3-pip
python3-devel
git-lfs
wget2-wget
jq

# Archive tools
tar
unzip
p7zip
p7zip-plugins

# Calculator
bc

# System infrastructure (§3)
btrfs-progs
snapper
grub2-tools
firewalld
NetworkManager
NetworkManager-wifi
udisks2

# SELinux (§4.1)
selinux-policy-targeted
policycoreutils
policycoreutils-python-utils

# Sudo (§4.2)
sudo

# Misc system
dracut
plymouth
chrony

# Exclude unwanted
-fedora-bookmarks
-fedora-chromium-config
-mediawriter

%end

# =====================================================================
# Base post-install — system configuration shared by all profiles
# =====================================================================
%post --erroronfail

# --- Btrfs mount options: add compress=zstd to fstab (§3.1) ---
sed -i 's|subvol=@\b|subvol=@,compress=zstd:1|' /etc/fstab
sed -i 's|subvol=@home\b|subvol=@home,compress=zstd:1|' /etc/fstab

# --- Set zsh as default shell for new users (§8.2) ---
sed -i 's|^SHELL=.*|SHELL=/bin/zsh|' /etc/default/useradd
chsh -s /bin/zsh linta 2>/dev/null || true

# --- Configure sudo: wheel group has sudo access (§4.2) ---
echo '%wheel ALL=(ALL) ALL' > /etc/sudoers.d/wheel
chmod 0440 /etc/sudoers.d/wheel

# --- Weekly Btrfs scrub timer (maintenance) ---
cat > /etc/systemd/system/btrfs-scrub@.timer <<'UNIT'
[Unit]
Description=Weekly Btrfs scrub on %f

[Timer]
OnCalendar=monthly
RandomizedDelaySec=1d
Persistent=true

[Install]
WantedBy=timers.target
UNIT

cat > /etc/systemd/system/btrfs-scrub@.service <<'UNIT'
[Unit]
Description=Btrfs scrub on %f

[Service]
Type=oneshot
ExecStart=/usr/sbin/btrfs scrub start -B %f
IOSchedulingClass=idle
CPUSchedulingPolicy=idle
Nice=19
UNIT

systemctl enable btrfs-scrub@-.timer

# --- Weekly fstrim (§3.9) — already enabled via services line above ---

# --- Package cache pruning timer (§3.9) ---
cat > /etc/systemd/system/linta-cache-prune.timer <<'UNIT'
[Unit]
Description=Weekly package cache pruning

[Timer]
OnCalendar=weekly
RandomizedDelaySec=6h
Persistent=true

[Install]
WantedBy=timers.target
UNIT

cat > /etc/systemd/system/linta-cache-prune.service <<'UNIT'
[Unit]
Description=Remove cached packages older than 30 days

[Service]
Type=oneshot
ExecStart=/usr/bin/find /var/cache/dnf -type f -mtime +30 -delete
UNIT

systemctl enable linta-cache-prune.timer

# --- Weekly Btrfs snapshot (§3.2): Monday 00:00 UTC ---
cat > /etc/systemd/system/linta-weekly-snapshot.timer <<'UNIT'
[Unit]
Description=Weekly Btrfs snapshot (Monday 00:00 UTC)

[Timer]
OnCalendar=Mon *-*-* 00:00:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
UNIT

cat > /etc/systemd/system/linta-weekly-snapshot.service <<'UNIT'
[Unit]
Description=Create weekly Btrfs snapshot

[Service]
Type=oneshot
ExecStart=/usr/bin/snapper create --type=single --description="weekly-auto" --cleanup-algorithm=number
UNIT

systemctl enable linta-weekly-snapshot.timer

# --- Snapper config for root subvolume (§3.2) ---
snapper -c root create-config / 2>/dev/null || true
snapper -c root set-config "NUMBER_LIMIT=5" 2>/dev/null || true

# --- Disable root login (§4.2) ---
passwd -l root

# --- Linta release info ---
cat > /etc/linta-release <<'EOF'
NAME="Linta"
VERSION="25.1"
ID=linta
ID_LIKE=fedora
VARIANT_ID=PROFILE_PLACEHOLDER
HOME_URL="https://lintalinux.org"
SUPPORT_URL="https://lintalinux.org/docs"
EOF

# --- USB auto-mount via udisks2 (§11.2) ---
mkdir -p /etc/polkit-1/rules.d
cat > /etc/polkit-1/rules.d/10-udisks2-automount.rules <<'RULES'
polkit.addRule(function(action, subject) {
    if ((action.id == "org.freedesktop.udisks2.filesystem-mount-system" ||
         action.id == "org.freedesktop.udisks2.filesystem-mount") &&
        subject.isInGroup("wheel")) {
        return polkit.Result.YES;
    }
});
RULES

%end
