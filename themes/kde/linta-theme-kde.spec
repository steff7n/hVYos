Name:           linta-theme-kde
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux KDE Plasma theme
License:        GPL-3.0-or-later
URL:            https://lintalinux.org
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       plasma-workspace

%description
Linta Linux default KDE Plasma theme. Modern dark theme with teal accent,
coordinated color scheme for Plasma, Kvantum, and KDE applications.

%install
install -Dm644 linta.colors %{buildroot}%{_datadir}/color-schemes/Linta.colors
install -Dm755 apply.sh %{buildroot}%{_datadir}/linta/themes/linta-kde-default/apply.sh
install -Dm644 metadata.json %{buildroot}%{_datadir}/linta/themes/linta-kde-default/metadata.json

%files
%{_datadir}/color-schemes/Linta.colors
%{_datadir}/linta/themes/linta-kde-default/
