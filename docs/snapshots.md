# Btrfs Snapshot Management

Linta uses Btrfs snapshots for transactional package management and system recovery. Snapshots are created automatically and can be managed manually.

---

## How Linta Uses Snapshots

- **Transactional package manager:** Every DNF operation (install, update, remove) is atomic. A snapshot is taken before the transaction; if anything fails, the system rolls back to that snapshot.
- **Recovery:** Boot into a snapshot from the GRUB menu to restore the system to a prior state.

---

## Automatic Snapshots

| Trigger | Schedule |
|---------|----------|
| Package operations | Before every DNF transaction |
| Weekly backup | Monday 00:00 UTC |

The DNF plugin creates a snapshot before each transaction and updates the GRUB menu afterward.

---

## Listing Snapshots

```bash
$ linta-snapshots list
```

Shows all snapshots with numbers and timestamps.

JSON output:

```bash
$ linta-snapshots list --json
```

---

## Creating Manual Snapshots

```bash
$ linta-snapshots create -d "Before major upgrade"
```

Add a short description for later reference. Manual snapshots follow the same retention rules as automatic ones.

---

## Rolling Back

```bash
$ linta-snapshots rollback <number>
```

Replace `<number>` with the snapshot number from `linta-snapshots list`.

**What happens:**

1. A snapshot of the **current** state is created before rollback
2. The system is restored to the chosen snapshot
3. GRUB entries are updated
4. A reboot is required to use the rolled-back system

---

## GRUB Boot Menu

The last **5 snapshots** appear in the GRUB menu at boot. Select one to boot into that snapshot instead of the current system.

- Default entry: current system
- Additional entries: snapshot 1, 2, 3, 4, 5 (newest first)

---

## Comparing Snapshots

```bash
$ linta-snapshots diff <number>
```

Shows changes between the current system and the specified snapshot (e.g. added/removed files).

---

## Backup via Btrfs Send/Receive

For off-site or external backups:

1. Create a snapshot: `linta-snapshots create -d "backup"`
2. Use `btrfs send` to stream the snapshot to another Btrfs filesystem:

```bash
$ sudo btrfs send /path/to/snapshot | btrfs receive /path/to/backup/destination
```

Or to a file on an external drive:

```bash
$ sudo btrfs send /path/to/snapshot | gzip > /mnt/external/backup.img.gz
```

---

## Retention

The GRUB menu shows the last 5 snapshots. Older snapshots are cleaned automatically; only the most recent 5 remain available at boot. The full snapshot history may still exist on disk until pruned by retention logic.
