# Linta build system

## Quick start (with container)

From project root:

```bash
# Build the Fedora-based builder image (one-time)
./scripts/build-with-container.sh help

# Validate manifests and kickstarts
./scripts/build-with-container.sh validate

# Run unit tests
./scripts/build-with-container.sh test

# Build all Linta RPMs
./scripts/build-with-container.sh build-rpm-all

# Create local YUM repo from built RPMs (for ISO builds)
./scripts/build-with-container.sh create-repo

# Build an ISO (requires --privileged, --network=host, and loop module)
sudo modprobe loop   # one-time, needed for livecd-creator loopback mounts
podman run --rm --privileged --network=host -v "$(pwd):/workspace:z" linta-builder build-iso kde
```

Use `LINTA_CONTAINER_RUNTIME=docker` if you use Docker instead of Podman.

## Output layout

- `build/output/rpms/` — built RPMs and SRPMs
- `build/output/repo/` — local YUM repo (after `create-repo`)
- `build/output/iso/` — built ISOs and logs

## Mock (optional)

A mock config for Fedora 42 is in `build/mock/linta-fc42-x86_64.cfg`. Use it with `mock -r linta-fc42-x86_64 ...` when building outside the container.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR:

- Validate manifests and kickstarts
- Run Python unit tests
- Build the container and run validate+test inside it
