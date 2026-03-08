Name:           linta-theme-niri
Version:        0.1.0
Release:        1%{?dist}
Summary:        Linta Linux Niri rice presets
License:        GPL-3.0-or-later
URL:            https://lintalinux.org

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       waybar
Requires:       mako
Requires:       fuzzel
Requires:       swaylock
Requires:       swaybg

%description
Curated visual presets (rices) for the Niri compositor on Linta Linux.
Each rice is a complete, coordinated theme: waybar, mako notifications,
fuzzel launcher, swaylock, and color palette.

Included rices:
- Dusk: warm dark (navy/amber)
- Frost: cool dark (midnight/ice blue)
- Forest: earthy dark (green/emerald)
- Ember: high-contrast dark (charcoal/orange)

%install
for rice in rice-1 rice-2 rice-3 rice-4; do
    rice_dest="%{buildroot}%{_datadir}/linta/themes/linta-niri-${rice}"
    mkdir -p "${rice_dest}/waybar" "${rice_dest}/mako" \
             "${rice_dest}/fuzzel" "${rice_dest}/swaylock"
    cp "${rice}/metadata.json" "${rice_dest}/"
    cp "${rice}/apply.sh" "${rice_dest}/"
    chmod 755 "${rice_dest}/apply.sh"
    cp "${rice}/waybar/config.jsonc" "${rice_dest}/waybar/"
    cp "${rice}/waybar/style.css" "${rice_dest}/waybar/"
    cp "${rice}/mako/config" "${rice_dest}/mako/"
    cp "${rice}/fuzzel/fuzzel.ini" "${rice_dest}/fuzzel/"
    cp "${rice}/swaylock/config" "${rice_dest}/swaylock/"
done

%files
%{_datadir}/linta/themes/linta-niri-rice-1/
%{_datadir}/linta/themes/linta-niri-rice-2/
%{_datadir}/linta/themes/linta-niri-rice-3/
%{_datadir}/linta/themes/linta-niri-rice-4/

%changelog
* Sun Mar 08 2026 Linta Project <dev@lintalinux.org> - 0.1.0-1
- Initial release: 4 Niri rices (Dusk, Frost, Forest, Ember)
