#!/bin/bash
set -euo pipefail

# Linta Linux — ISO Build Script
# Builds a bootable installation ISO for a given profile using livemedia-creator.
#
# Usage: ./scripts/build-iso.sh <profile> [fedora-version]
#
# Profiles: bare, kde, niri, combined
# Requires: lorax (livemedia-creator), anaconda, pykickstart
# Must be run as root (or via sudo).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
KICKSTART_DIR="${PROJECT_ROOT}/build/kickstart"
OUTPUT_DIR="${PROJECT_ROOT}/build/output"

PROFILE="${1:-}"
FEDORA_VERSION="${2:-42}"

VALID_PROFILES="bare kde niri combined"

usage() {
    echo "Usage: $0 <profile> [fedora-version]"
    echo ""
    echo "Profiles: ${VALID_PROFILES}"
    echo "Fedora version: defaults to ${FEDORA_VERSION}"
    echo ""
    echo "Examples:"
    echo "  $0 bare          # Build Bare ISO (Fedora 42)"
    echo "  $0 kde           # Build KDE ISO (Fedora 42)"
    echo "  $0 niri 41       # Build Niri ISO with Fedora 41 (override)"
    echo ""
    echo "Requirements:"
    echo "  - Must be run as root (sudo)"
    echo "  - Packages: lorax pykickstart anaconda"
    echo "  - At least 10 GB free disk space"
    exit 1
}

if [[ -z "${PROFILE}" ]]; then
    usage
fi

if ! echo "${VALID_PROFILES}" | grep -qw "${PROFILE}"; then
    echo "Error: invalid profile '${PROFILE}'"
    echo "Valid profiles: ${VALID_PROFILES}"
    exit 1
fi

if [[ "$(id -u)" -ne 0 ]]; then
    echo "Error: this script must be run as root (sudo $0 $*)"
    exit 1
fi

KICKSTART_FILE="${KICKSTART_DIR}/linta-${PROFILE}.ks"
if [[ ! -f "${KICKSTART_FILE}" ]]; then
    echo "Error: kickstart file not found: ${KICKSTART_FILE}"
    exit 1
fi

# Check dependencies
for cmd in livemedia-creator ksflatten; do
    if ! command -v "${cmd}" &>/dev/null; then
        echo "Error: '${cmd}' not found. Install lorax and pykickstart:"
        echo "  dnf install lorax pykickstart anaconda"
        exit 1
    fi
done

TIMESTAMP="$(date +%Y%m%d)"
ISO_LABEL="Linta-${PROFILE}-${FEDORA_VERSION}-${TIMESTAMP}"
ISO_NAME="linta-${PROFILE}-${FEDORA_VERSION}-x86_64-${TIMESTAMP}.iso"

WORK_DIR="${OUTPUT_DIR}/work-${PROFILE}"
FLAT_KS="${WORK_DIR}/flat-${PROFILE}.ks"

echo "============================================"
echo " Linta ISO Builder"
echo "============================================"
echo " Profile:        ${PROFILE}"
echo " Fedora base:    ${FEDORA_VERSION}"
echo " Kickstart:      ${KICKSTART_FILE}"
echo " Output:         ${OUTPUT_DIR}/${ISO_NAME}"
echo " Work dir:       ${WORK_DIR}"
echo "============================================"
echo ""

mkdir -p "${OUTPUT_DIR}" "${WORK_DIR}"

echo "[1/4] Flattening kickstart file..."
ksflatten -c "${KICKSTART_FILE}" -o "${FLAT_KS}" \
    --version "F${FEDORA_VERSION}"

# Substitute $releasever in the flattened kickstart
sed -i "s|\$releasever|${FEDORA_VERSION}|g" "${FLAT_KS}"

if ! grep -q 'cp -a.*/usr/lib/modules.*vmlinuz' "${FLAT_KS}"; then
    echo "Error: ksflatten dropped the vmlinuz/initramfs boot fix from the"
    echo "       flattened kickstart. The resulting ISO would not boot."
    echo "       Check that linta-base.ks boot-artifact %post uses no percent"
    echo "       signs in shell expansion (pykickstart misparses them)."
    exit 1
fi

echo "[2/4] Validating kickstart..."
ksvalidator "${FLAT_KS}" || {
    echo "Warning: kickstart validation reported issues (may be non-fatal)"
}

echo "[3/4] Building ISO with livemedia-creator..."
echo "       This will take a while (20-60 minutes depending on profile and network)."
echo ""

livemedia-creator \
    --ks="${FLAT_KS}" \
    --no-virt \
    --make-iso \
    --resultdir="${OUTPUT_DIR}" \
    --project="Linta" \
    --releasever="${FEDORA_VERSION}" \
    --volid="${ISO_LABEL}" \
    --iso-only \
    --iso-name="${ISO_NAME}" \
    --tmp="${WORK_DIR}" \
    2>&1 | tee "${OUTPUT_DIR}/build-${PROFILE}.log"

echo ""
echo "[4/4] Build complete."

if [[ -f "${OUTPUT_DIR}/${ISO_NAME}" ]]; then
    ISO_SIZE="$(du -h "${OUTPUT_DIR}/${ISO_NAME}" | cut -f1)"
    SHA256="$(sha256sum "${OUTPUT_DIR}/${ISO_NAME}" | cut -d' ' -f1)"

    echo ""
    echo "============================================"
    echo " Build successful!"
    echo "============================================"
    echo " ISO:      ${OUTPUT_DIR}/${ISO_NAME}"
    echo " Size:     ${ISO_SIZE}"
    echo " SHA256:   ${SHA256}"
    echo "============================================"

    echo "${SHA256}  ${ISO_NAME}" > "${OUTPUT_DIR}/${ISO_NAME}.sha256"
    echo " Checksum: ${OUTPUT_DIR}/${ISO_NAME}.sha256"
else
    echo "Error: ISO file was not created."
    echo "Check the build log: ${OUTPUT_DIR}/build-${PROFILE}.log"
    exit 1
fi

echo ""
echo "To test in QEMU:"
echo "  qemu-system-x86_64 -m 4096 -cdrom ${OUTPUT_DIR}/${ISO_NAME} -boot d -enable-kvm"
