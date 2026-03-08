Name:           linta-config-system
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux system-level configuration and timers
License:        GPL-3.0-or-later
URL:            https://lintalinux.org

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       systemd
Requires:       btrfs-progs
Requires:       snapper
Requires:       linta-snapshots

%description
System-level configuration for Linta Linux. Includes:
- Weekly Btrfs snapshot timer (Monday 00:00 UTC)
- Package cache pruning timer (weekly, 30-day retention)
- Monthly Btrfs scrub timer

%install
install -Dm644 system/linta-weekly-snapshot.timer \
    %{buildroot}%{_unitdir}/linta-weekly-snapshot.timer
install -Dm644 system/linta-weekly-snapshot.service \
    %{buildroot}%{_unitdir}/linta-weekly-snapshot.service
install -Dm644 system/linta-cache-prune.timer \
    %{buildroot}%{_unitdir}/linta-cache-prune.timer
install -Dm644 system/linta-cache-prune.service \
    %{buildroot}%{_unitdir}/linta-cache-prune.service
install -Dm644 system/btrfs-scrub@.timer \
    %{buildroot}%{_unitdir}/btrfs-scrub@.timer
install -Dm644 system/btrfs-scrub@.service \
    %{buildroot}%{_unitdir}/btrfs-scrub@.service

%post
%systemd_post linta-weekly-snapshot.timer
%systemd_post linta-cache-prune.timer
%systemd_post btrfs-scrub@-.timer

%preun
%systemd_preun linta-weekly-snapshot.timer
%systemd_preun linta-cache-prune.timer
%systemd_preun btrfs-scrub@-.timer

%files
%{_unitdir}/linta-weekly-snapshot.timer
%{_unitdir}/linta-weekly-snapshot.service
%{_unitdir}/linta-cache-prune.timer
%{_unitdir}/linta-cache-prune.service
%{_unitdir}/btrfs-scrub@.timer
%{_unitdir}/btrfs-scrub@.service

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release: snapshot, cache prune, and scrub timers
