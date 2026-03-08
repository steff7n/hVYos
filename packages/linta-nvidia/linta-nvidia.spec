Name:           linta-nvidia
Version:        0.1.0
Release:        1%{?dist}
Summary:        NVIDIA GPU setup tool for Linta Linux
License:        GPL-3.0-or-later
URL:            https://lintalinux.org

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3 >= 3.12
Requires:       pciutils
Requires:       dnf

%description
Dedicated NVIDIA GPU setup tool for Linta Linux. Detects NVIDIA GPUs,
installs proprietary drivers via RPM Fusion + akmod, configures DKMS,
sets Wayland compatibility flags, and handles hybrid GPU (PRIME) setup.

Invoked via: linta-nvidia setup | status | uninstall
Or via: lintactl nvidia

%prep
%autosetup

%build
# Pure Python, no build step

%install
install -Dm755 linta_nvidia.py %{buildroot}%{_bindir}/linta-nvidia

%files
%{_bindir}/linta-nvidia

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release: status, setup (RPM Fusion + akmod), uninstall, hybrid GPU
