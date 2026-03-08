Name:           linta-theme-plymouth
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux Plymouth boot splash
License:        GPL-3.0-or-later
URL:            https://lintalinux.org
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       plymouth

%description
Minimal branded boot splash for Linta Linux. Shows distro logo with
progress indicator.

%install
mkdir -p %{buildroot}%{_datadir}/plymouth/themes/linta
cp -r linta.plymouth linta.script %{buildroot}%{_datadir}/plymouth/themes/linta/

%post
plymouth-set-default-theme linta 2>/dev/null || true

%files
%{_datadir}/plymouth/themes/linta/
