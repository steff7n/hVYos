#!/bin/bash
set -euo pipefail

# Linta Linux — ISO boot test
# Boots an ISO in QEMU/KVM and checks if it reaches a usable state.
# Uses a timeout — if the VM doesn't reach target within N seconds, it fails.

ISO="${1:-}"
TIMEOUT="${2:-120}"

if [[ -z "${ISO}" ]]; then
    echo "Usage: $0 <iso-path> [timeout-seconds]"
    echo ""
    echo "Boots the ISO in QEMU and checks if it starts successfully."
    echo "Default timeout: 120 seconds."
    exit 1
fi

if [[ ! -f "${ISO}" ]]; then
    echo "Error: ISO not found: ${ISO}"
    exit 1
fi

if ! command -v qemu-system-x86_64 &>/dev/null; then
    echo "Error: qemu-system-x86_64 not found."
    echo "  dnf install qemu-system-x86-core"
    exit 1
fi

echo "Linta ISO Boot Test"
echo "==================="
echo "  ISO:     ${ISO}"
echo "  Timeout: ${TIMEOUT}s"
echo ""

SERIAL_LOG="$(mktemp)"

echo "Starting QEMU (headless, serial console)..."
timeout "${TIMEOUT}" qemu-system-x86_64 \
    -m 2048 \
    -cdrom "${ISO}" \
    -boot d \
    -nographic \
    -serial file:"${SERIAL_LOG}" \
    -no-reboot \
    -enable-kvm 2>/dev/null &

QEMU_PID=$!

echo "QEMU PID: ${QEMU_PID}"
echo "Waiting for boot (max ${TIMEOUT}s)..."

sleep "${TIMEOUT}" 2>/dev/null || true
kill "${QEMU_PID}" 2>/dev/null || true
wait "${QEMU_PID}" 2>/dev/null || true

if grep -qi "login\|Welcome to\|systemd.*Reached target" "${SERIAL_LOG}" 2>/dev/null; then
    echo ""
    echo "PASS: ISO booted successfully (found login/systemd target in serial output)."
    rm -f "${SERIAL_LOG}"
    exit 0
else
    echo ""
    echo "FAIL: ISO did not reach expected boot state within ${TIMEOUT}s."
    echo "Serial output (last 20 lines):"
    tail -20 "${SERIAL_LOG}" 2>/dev/null
    rm -f "${SERIAL_LOG}"
    exit 1
fi
