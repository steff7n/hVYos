Name:           floorp
Version:        11.19.1
Release:        1%{?dist}
Summary:        Firefox-based browser with sidebar tabs and workspaces
License:        MPL-2.0
URL:            https://floorp.app
Source0:        https://github.com/nicoyuki/nicoyuki/releases/download/v%{version}/floorp-%{version}.linux-x86_64.tar.bz2

ExclusiveArch:  x86_64

%description
Floorp is a Firefox-based browser with built-in sidebar tabs, workspaces,
and high customization. Linta ships it as the default browser.

%prep
%setup -q -n floorp

%install
mkdir -p %{buildroot}/opt/floorp
cp -r * %{buildroot}/opt/floorp/
mkdir -p %{buildroot}%{_bindir}
ln -s /opt/floorp/floorp %{buildroot}%{_bindir}/floorp
install -Dm644 browser/chrome/icons/default/default128.png \
    %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/floorp.png

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/floorp.desktop << 'DESKTOP'
[Desktop Entry]
Name=Floorp
Comment=Firefox-based web browser
Exec=floorp %u
Icon=floorp
Terminal=false
Type=Application
MimeType=text/html;text/xml;application/xhtml+xml;application/xml;
Categories=Network;WebBrowser;
DESKTOP

%files
/opt/floorp/
%{_bindir}/floorp
%{_datadir}/applications/floorp.desktop
%{_datadir}/icons/hicolor/128x128/apps/floorp.png

%changelog
* Mon Mar 09 2026 Linta Project <dev@lintalinux.org> - 11.19.1-1
- Initial Linta package
