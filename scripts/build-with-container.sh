#!/bin/bash
set -euo pipefail

# Linta — Build using container (Podman or Docker)
# Run from project root. Mounts current dir as /workspace.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
IMAGE_NAME="${LINTA_BUILD_IMAGE:-linta-builder}"
RUNTIME="${LINTA_CONTAINER_RUNTIME:-podman}"

if ! command -v "${RUNTIME}" &>/dev/null; then
    echo "Error: ${RUNTIME} not found. Install podman or set LINTA_CONTAINER_RUNTIME=docker"
    exit 1
fi

# Build image if missing
if ! "${RUNTIME}" image exists "${IMAGE_NAME}" 2>/dev/null; then
    echo "Building Linta builder image (one-time)..."
    "${RUNTIME}" build -t "${IMAGE_NAME}" -f "${PROJECT_ROOT}/build/Containerfile" "${PROJECT_ROOT}/build"
    echo ""
fi

# Run with workspace mounted
"${RUNTIME}" run --rm \
    -v "${PROJECT_ROOT}:/workspace:z" \
    -w /workspace \
    "${IMAGE_NAME}" \
    "$@"
