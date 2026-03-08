#!/bin/bash
set -euo pipefail

# Linta Linux — Package manifest validator
# Checks that all packages listed in build/packages/*.txt exist
# in Fedora repositories or are custom Linta packages.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST_DIR="${SCRIPT_DIR}/../packages"
FAIL_COUNT=0
PASS_COUNT=0
SKIP_COUNT=0

echo "Linta Package Manifest Validator"
echo "================================="
echo ""

for manifest in "${MANIFEST_DIR}"/*.txt; do
    filename="$(basename "${manifest}")"
    echo "--- ${filename} ---"

    while IFS= read -r line; do
        line="$(echo "${line}" | sed 's/#.*//' | xargs)"
        [[ -z "${line}" ]] && continue

        if [[ "${line}" == linta-* ]] || [[ "${line}" == lintactl ]]; then
            echo "  SKIP (custom): ${line}"
            ((SKIP_COUNT++))
            continue
        fi

        if dnf info --available "${line}" &>/dev/null; then
            echo "  PASS: ${line}"
            ((PASS_COUNT++))
        else
            echo "  FAIL: ${line} — not found in repos"
            ((FAIL_COUNT++))
        fi
    done < "${manifest}"
    echo ""
done

echo "================================="
echo "Results: ${PASS_COUNT} passed, ${SKIP_COUNT} skipped (custom), ${FAIL_COUNT} failed"

if [[ ${FAIL_COUNT} -gt 0 ]]; then
    echo "VALIDATION FAILED: ${FAIL_COUNT} package(s) not found in Fedora repos."
    exit 1
else
    echo "All packages validated."
    exit 0
fi
