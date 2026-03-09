Name:           swaylock-effects
Version:        1.7.0.0
Release:        1%{?dist}
Summary:        Screen locker for Wayland with effects (fork of swaylock)
License:        MIT
URL:            https://github.com/jirutka/swaylock-effects
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  meson >= 0.59
BuildRequires:  gcc
BuildRequires:  pkg-config
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  cairo-devel
BuildRequires:  gdk-pixbuf2-devel
BuildRequires:  pam-devel
BuildRequires:  scdoc
Conflicts:      swaylock

%description
Fork of swaylock with additional visual effects: blur, pixel, vignette,
fade, screenshots. Used as the session locker on Linta's Niri profile.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%{_bindir}/swaylock
%{_sysconfdir}/pam.d/swaylock
%{_mandir}/man1/swaylock.1*
%{_datadir}/bash-completion/completions/swaylock
%{_datadir}/fish/vendor_completions.d/swaylock.fish
%{_datadir}/zsh/site-functions/_swaylock

%changelog
* Mon Mar 09 2026 Linta Project <dev@lintalinux.org> - 1.7.0.0-1
- Initial Linta package
