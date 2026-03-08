Name:           lintactl
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux system management tool
License:        GPL-3.0-or-later
URL:            https://lintalinux.org

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3 >= 3.12

%description
lintactl is the primary CLI tool for managing Linta-specific features:
theme switching, profile info, font wizard re-run, NVIDIA setup invocation,
and distro version display.

Does NOT wrap standard system tools (dnf, btrfs, systemctl).

%prep
%autosetup

%build
%py3_build

%install
%py3_install
install -Dm644 lintactl.py %{buildroot}%{_datadir}/linta/lintactl.py

%files
%{_bindir}/lintactl
%{python3_sitelib}/lintactl*
%dir %{_datadir}/linta

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release: info, profile, theme list/set, nvidia/font-wizard stubs
