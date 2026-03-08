Name:           linta-config-zsh
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux default zsh configuration
License:        GPL-3.0-or-later
URL:            https://lintalinux.org

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       zsh
Requires:       zsh-syntax-highlighting
Requires:       git
Requires:       curl

%description
Default zsh configuration for Linta Linux. Sets up oh-my-zsh with
Powerlevel10k theme, extract plugin, and sensible defaults.
oh-my-zsh and Powerlevel10k are installed on first login if not present.

%install
install -Dm644 zsh/zshrc %{buildroot}%{_sysconfdir}/skel/.zshrc

%files
%config(noreplace) %{_sysconfdir}/skel/.zshrc

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release
