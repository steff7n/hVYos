Name:           niri
Version:        0.1.9
Release:        1%{?dist}
Summary:        Scrollable tiling Wayland compositor
License:        GPL-3.0-or-later
URL:            https://github.com/YaLTeR/niri
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cargo >= 1.75
BuildRequires:  gcc
BuildRequires:  pkg-config
BuildRequires:  clang-devel
BuildRequires:  libwayland-client-devel
BuildRequires:  libwayland-server-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  libinput-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  mesa-libgbm-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  libseat-devel
BuildRequires:  pipewire-devel
BuildRequires:  pango-devel
BuildRequires:  cairo-devel
BuildRequires:  systemd-devel

%description
A scrollable-tiling Wayland compositor. Windows are arranged in columns
on an infinite strip. Opening new windows never shifts existing ones.

%prep
%autosetup

%build
cargo build --release --locked

%install
install -Dm755 target/release/niri %{buildroot}%{_bindir}/niri
install -Dm755 target/release/niri-session %{buildroot}%{_bindir}/niri-session
install -Dm644 resources/niri-session %{buildroot}%{_datadir}/wayland-sessions/niri.desktop
install -Dm644 resources/niri-portals.conf %{buildroot}%{_datadir}/xdg-desktop-portal/niri-portals.conf

%files
%license LICENSE
%{_bindir}/niri
%{_bindir}/niri-session
%{_datadir}/wayland-sessions/niri.desktop
%{_datadir}/xdg-desktop-portal/niri-portals.conf

%changelog
* Mon Mar 09 2026 Linta Project <dev@lintalinux.org> - 0.1.9-1
- Initial Linta package
