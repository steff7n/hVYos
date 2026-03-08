Name:           linta-flatpak-manager
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux Flatpak management application
License:        GPL-3.0-or-later
URL:            https://lintalinux.org
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3 >= 3.12
Requires:       python3-qt6
Requires:       flatpak

%description
Custom Flatpak management GUI for Linta Linux. Browse Flathub, install/update/remove
Flatpak applications, and manage permissions. Themed to match Linta's visual identity.

%install
install -Dm755 linta_flatpak_manager.py %{buildroot}%{_bindir}/linta-flatpak-manager
install -Dm644 linta-flatpak-manager.desktop %{buildroot}%{_datadir}/applications/linta-flatpak-manager.desktop

%files
%{_bindir}/linta-flatpak-manager
%{_datadir}/applications/linta-flatpak-manager.desktop

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release
