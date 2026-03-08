# Linta Installer

TUI (ncurses) installer for Linta Linux.

## Screens

1. Welcome
2. Profile selection (KDE, Niri, Combined, Bare)
3. Hostname (auto-generated memorable name, editable)
4. Locale selection
5. Timezone selection
6. Disk encryption (LUKS2, opt-in)
7. Disk selection
8. Confirmation summary
9. Installation progress
10. Complete

## Disk Layout

- EFI System Partition: 512 MB (FAT32)
- /boot: 1 GB (ext4)
- Root: remaining space (Btrfs)
  - Subvolume @: mounted at /
  - Subvolume @home: mounted at /home
  - Compression: zstd

## Profiles

Creates systems for: **[All]** profiles

## Spec Reference

README.md §10.1
