# linta-snapshots

Btrfs snapshot management for Linta Linux.

## Commands

| Command | Description |
|---|---|
| `linta-snapshots list` | List all snapshots |
| `linta-snapshots list --json` | List snapshots as JSON |
| `linta-snapshots create [-d "desc"]` | Create a manual snapshot |
| `linta-snapshots rollback <number>` | Rollback to a snapshot (creates pre-rollback snapshot first) |
| `linta-snapshots grub-update` | Regenerate GRUB menu entries for last 5 snapshots |
| `linta-snapshots diff <number>` | Show changes between current system and snapshot |

## DNF Plugin

The included DNF plugin (`dnf_plugin_linta_snapshot.py`) automatically creates
a snapshot before every package transaction (install, update, remove). After
the transaction, it updates the GRUB snapshot menu.

## Profiles

Applies to: **[All]**

## Spec Reference

README.md §2.1, §3.2, §6.1
