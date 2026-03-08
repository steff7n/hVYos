Name:           linta-theme-sddm
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux SDDM login theme
License:        GPL-3.0-or-later
URL:            https://lintalinux.org
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       sddm

%description
Linta Linux branded SDDM login theme. Dark theme with teal accent,
clean login form.

%install
mkdir -p %{buildroot}%{_datadir}/sddm/themes/linta
cp -r Main.qml metadata.desktop theme.conf %{buildroot}%{_datadir}/sddm/themes/linta/

%files
%{_datadir}/sddm/themes/linta/
