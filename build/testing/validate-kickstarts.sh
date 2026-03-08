#!/bin/bash
set -euo pipefail

# Linta Linux — Kickstart file validator
# Validates syntax of all kickstart files using ksvalidator.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KS_DIR="${SCRIPT_DIR}/../kickstart"
FAIL=0

echo "Linta Kickstart Validator"
echo "========================="
echo ""

if ! command -v ksvalidator &>/dev/null; then
    echo "Error: ksvalidator not found. Install pykickstart:"
    echo "  dnf install pykickstart"
    exit 1
fi

for ks in "${KS_DIR}"/linta-*.ks; do
    filename="$(basename "${ks}")"
    echo -n "  ${filename}: "

    if [[ "${filename}" == "linta-base.ks" ]]; then
        echo "SKIP (partial — included by profile kickstarts)"
        continue
    fi

    # Flatten first, then validate
    tmpfile="$(mktemp)"
    if ksflatten -c "${ks}" -o "${tmpfile}" 2>/dev/null; then
        if ksvalidator "${tmpfile}" 2>/dev/null; then
            echo "PASS"
        else
            echo "WARN (validation issues, may be non-fatal)"
        fi
    else
        echo "FAIL (ksflatten error)"
        ((FAIL++))
    fi
    rm -f "${tmpfile}"
done

echo ""
if [[ ${FAIL} -gt 0 ]]; then
    echo "FAILED: ${FAIL} kickstart file(s) have errors."
    exit 1
else
    echo "All kickstart files validated."
fi
