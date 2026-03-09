Name:           linta-keybindings
Version:        0.1.0
Release:        1%{?dist}
Summary:        Searchable keybinding reference overlay for Linta Linux
License:        GPL-3.0-or-later
URL:            https://lintalinux.org
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3 >= 3.12
Requires:       python3-qt6

%description
Searchable keybinding reference overlay for Linta Linux. Activated by a hotkey,
shows a filterable list of all keybindings for the current desktop environment
(KDE Plasma or Niri compositor).

%prep
%autosetup

%build
# Pure Python, no build step

%install
install -Dm755 linta_keybindings.py %{buildroot}%{_bindir}/linta-keybindings

%files
%{_bindir}/linta-keybindings

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release: Niri KDL parser, KDE shortcuts parser, overlay UI
