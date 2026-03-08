Name:           linta-snapshots
Version:        0.1.0
Release:        1%{?dist}
Summary:        Btrfs snapshot management for Linta Linux
License:        GPL-3.0-or-later
URL:            https://lintalinux.org

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3 >= 3.12
Requires:       snapper
Requires:       btrfs-progs
Requires:       grub2-tools

%description
Btrfs snapshot management for Linta Linux. Provides:
- CLI for listing, creating, and rolling back snapshots
- DNF plugin for automatic pre-transaction snapshots
- GRUB menu integration showing last 5 snapshots
- Works with snapper as the backend

%prep
%autosetup

%build
# No build step — pure Python

%install
install -Dm755 linta_snapshots.py %{buildroot}%{_bindir}/linta-snapshots
install -Dm644 dnf_plugin_linta_snapshot.py \
    %{buildroot}%{python3_sitelib}/dnf-plugins/linta_snapshot.py

%files
%{_bindir}/linta-snapshots
%{python3_sitelib}/dnf-plugins/linta_snapshot.py

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release: list, create, rollback, grub-update, diff, DNF plugin
