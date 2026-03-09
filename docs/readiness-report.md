# Linta — Readiness report (lead)

**Last updated:** 2025-03 (session)  
**Purpose:** What is done vs what blocks "distro ready" for the first milestone ISO.

---

## Done (green)

| Area | Status |
|------|--------|
| Phases 0–8 | Implemented: scaffolding, kickstarts, all 6 custom packages, configs, themes, welcome, flatpak-manager, keybindings, TUI installer, docs |
| Unit tests | 95 tests across lintactl, snapshots, nvidia, welcome, flatpak-manager, keybindings, installer, build-with-container |
| Bug hunt | 8/8 fixes in main (path traversal, GRUB UUID, info fs label, RPM Fusion URL, NVMe partition, welcome marker, Docker image check, keybindings primary screen) |
| CI | GitHub Actions: validate-and-test (host), container-build-and-test; validate only in container |
| Build system | Containerfile, container-entry.sh, build-with-container.sh, mock config, create-repo, build-iso wiring |
| Release checklist | `docs/release-checklist.md` — criteria and sign-off for first milestone |

---

## Blockers / to verify (red / yellow)

| Item | Notes |
|------|--------|
| **ISO build in container** | Not run in this session (no podman/docker on host). **Action:** On a machine with Podman: run `./scripts/build-with-container.sh build-rpm-all`, then `create-repo`, then `podman run --rm --privileged -v $(pwd):/workspace:z linta-builder build-iso kde`. Fix any build/lorax/kickstart errors. |
| **ISO boot test** | No automated or manual boot test was run. **Action:** Boot the built ISO in QEMU or real hardware; confirm installer and first-boot path. |
| **Validate in Fedora env** | `make validate` (manifest + kickstart) passes only in container or on Fedora (dnf + ksvalidator). **Action:** Already delegated to container job in CI; for local check use container. |
| **Wallpapers / logos** | `themes/wallpapers/` and optional Plymouth/SDDM assets are for you to add. Not a hard blocker if placeholders are acceptable for first milestone. |

---

## Conclusion

- **Code and automation:** Ready for a first milestone (Phases 0–8 implemented, tests and CI green, checklist in place).
- **Artifacts:** First milestone is **not** signed off until:
  1. At least one ISO is built successfully in the container.
  2. That ISO has been boot-tested (install + first-boot).

**Next lead action:** Run the container ISO build on a host with Podman/Docker; fix any failures; then run a boot test and tick the checklist in `docs/release-checklist.md`.
