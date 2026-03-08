Name:           linta-welcome
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux first-boot welcome application
License:        GPL-3.0-or-later
URL:            https://lintalinux.org

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3 >= 3.12
Requires:       python3-qt6
Requires:       lintactl
Requires:       dnf

%description
First-boot welcome wizard for Linta Linux. Guides users through:
- Terminal emulator selection (WezTerm, Alacritty, Kitty, foot, Ghostty, Tilix, Terminator)
- File manager selection (Dolphin, Thunar, Nautilus, PCManFM-Qt, nnn, ranger, yazi)
- Font wizard with 4 preset tiers (Comprehensive, Standard, Per-Locale, Bare Minimum)
- Theme picker (Niri rices or KDE theme)
- Timezone/locale confirmation
- Quick tips

%prep
%autosetup

%build
# Pure Python, no build step

%install
install -Dm755 linta_welcome.py %{buildroot}%{_bindir}/linta-welcome
install -Dm644 linta-welcome-firstboot.service \
    %{buildroot}%{_userunitdir}/linta-welcome-firstboot.service
install -Dm644 linta-welcome.desktop \
    %{buildroot}%{_sysconfdir}/xdg/autostart/linta-welcome.desktop

%files
%{_bindir}/linta-welcome
%{_userunitdir}/linta-welcome-firstboot.service
%{_sysconfdir}/xdg/autostart/linta-welcome.desktop

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release: full wizard with terminal, file manager, font, theme, locale pages
