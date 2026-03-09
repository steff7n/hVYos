Name:           linta-config-niri
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux default Niri compositor configuration
License:        GPL-3.0-or-later
URL:            https://lintalinux.org
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

%description
Default Niri compositor configuration for Linta Linux. Provides sensible
keybindings, layout defaults (gaps, focus ring), and startup programs
(waybar, swaybg).

%install
install -Dm644 niri/config.kdl %{buildroot}%{_sysconfdir}/skel/.config/niri/config.kdl

%files
%config(noreplace) %{_sysconfdir}/skel/.config/niri/config.kdl

%changelog
* Mon Mar 09 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release
