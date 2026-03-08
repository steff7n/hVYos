Name:           linta-config-helix
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux default Helix editor configuration
License:        GPL-3.0-or-later
URL:            https://lintalinux.org

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

%description
Default Helix editor configuration for Linta Linux. Provides sensible
defaults: relative line numbers, auto-save, LSP inlay hints, indent guides.

%install
install -Dm644 helix/config.toml %{buildroot}%{_sysconfdir}/skel/.config/helix/config.toml

%files
%config(noreplace) %{_sysconfdir}/skel/.config/helix/config.toml

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release
