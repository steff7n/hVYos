Name:           linta-installer
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux TUI installer
License:        GPL-3.0-or-later
URL:            https://lintalinux.org
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3 >= 3.12
Requires:       parted
Requires:       btrfs-progs
Requires:       cryptsetup
Requires:       dnf
Requires:       grub2-tools
Requires:       grub2-efi-x64

%description
TUI (ncurses) installer for Linta Linux. Guides users through profile
selection, hostname, locale, timezone, disk encryption, and partitioning
with Btrfs subvolumes.

%install
install -Dm755 linta_installer.py %{buildroot}%{_bindir}/linta-installer

%files
%{_bindir}/linta-installer

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release: full TUI installation wizard
