# Linta Linux — Base Kickstart Configuration
# Shared by all profiles. Do NOT use this file directly —
# use a profile-specific .ks that %include's this.
#
# Profiles: [All]
# Spec reference: README.md §1–§4, §8.2, §11

# --- Installation source ---
# livemedia-creator --make-iso requires a url install method.
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
bootloader --timeout=5 --append="rhgb quiet console=ttyS0,115200n8"

# --- Disk layout ---
# Single root partition: lorax extracts everything from it to build the ISO.
# Separate /boot/efi would put EFI files on a partition lorax can't reach.
# The TUI installer does its own Btrfs+EFI layout on the real disk.
zerombr
clearpart --all --initlabel
part / --size=12000 --fstype=ext4

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

# Archive tools (@core provides tar)
unzip
p7zip
p7zip-plugins

# Calculator
bc

# System infrastructure (§3)
btrfs-progs
snapper
grub2-tools
grub2-efi-x64
grub2-efi-x64-modules
grub2-efi-x64-cdboot
grub2-pc-modules
shim-x64
efibootmgr
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
dracut-live
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
# (skip on live ISO which uses ext4)
if findmnt -n -o FSTYPE / | grep -q btrfs; then
  sed -i 's|subvol=@\b|subvol=@,compress=zstd:1|' /etc/fstab
  sed -i 's|subvol=@home\b|subvol=@home,compress=zstd:1|' /etc/fstab
fi

# --- Set zsh as default shell for new users (§8.2) ---
sed -i 's|^SHELL=.*|SHELL=/bin/zsh|' /etc/default/useradd
chsh -s /bin/zsh linta 2>/dev/null || true

# --- Configure sudo: wheel group has sudo access (§4.2) ---
echo '%wheel ALL=(ALL) ALL' > /etc/sudoers.d/wheel
chmod 0440 /etc/sudoers.d/wheel

# --- Weekly Btrfs scrub timer (maintenance) — only on btrfs ---
if findmnt -n -o FSTYPE / | grep -q btrfs; then
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
fi

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

# --- Weekly Btrfs snapshot (§3.2): Monday 00:00 UTC — only on btrfs ---
if findmnt -n -o FSTYPE / | grep -q btrfs; then
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
fi

# --- Snapper config for root subvolume (§3.2) — only on btrfs ---
findmnt -n -o FSTYPE / | grep -q btrfs && snapper -c root create-config / 2>/dev/null || true
findmnt -n -o FSTYPE / | grep -q btrfs && snapper -c root set-config "NUMBER_LIMIT=5" 2>/dev/null || true

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

# =====================================================================
# Boot artifacts — ensure vmlinuz + initramfs exist in /boot.
# Kept in a separate %post section so ksflatten cannot silently drop it
# (the previous inline version used shell parameter expansion with the
# percent sign, which pykickstart mis-parses as a section delimiter).
# =====================================================================
%post
for kdir in /lib/modules/*/; do
  kver=$(basename "$kdir")
  [ "$kver" = "*" ] && break
  if [ -f "/usr/lib/modules/${kver}/vmlinuz" ] && [ ! -f "/boot/vmlinuz-${kver}" ]; then
    cp -a "/usr/lib/modules/${kver}/vmlinuz" "/boot/vmlinuz-${kver}"
  fi
  [ -f "/boot/initramfs-${kver}.img" ] || \
    dracut -f --no-hostonly "/boot/initramfs-${kver}.img" "$kver" 2>/dev/null || true
done
%end
