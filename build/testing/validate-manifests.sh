#!/bin/bash
set -uo pipefail

# Linta Linux — Package manifest validator
# Checks that all packages listed in build/packages/*.txt exist
# in Fedora repositories or are custom Linta packages.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST_DIR="${SCRIPT_DIR}/../packages"
UPSTREAM_SPECS_DIR="${SCRIPT_DIR}/../../build/packages/specs"
FAIL_COUNT=0
PASS_COUNT=0
SKIP_COUNT=0

echo "Linta Package Manifest Validator"
echo "================================="
echo ""

ALL_PKGS=()
declare -A PKG_SOURCE

for manifest in "${MANIFEST_DIR}"/*.txt; do
    filename="$(basename "${manifest}")"

    while IFS= read -r line; do
        line="$(echo "${line}" | sed 's/#.*//' | xargs)"
        [[ -z "${line}" ]] && continue

        if [[ "${line}" == linta-* ]] || [[ "${line}" == lintactl ]] || [[ -f "${UPSTREAM_SPECS_DIR}/${line}.spec" ]]; then
            SKIP_COUNT=$((SKIP_COUNT + 1))
            PKG_SOURCE["${line}"]="SKIP"
            continue
        fi

        ALL_PKGS+=("${line}")
        PKG_SOURCE["${line}"]="${filename}"
    done < "${manifest}"
done

if [[ ${#ALL_PKGS[@]} -gt 0 ]]; then
    UNIQUE_PKGS=($(printf '%s\n' "${ALL_PKGS[@]}" | sort -u))

    echo "Checking ${#UNIQUE_PKGS[@]} packages against Fedora repos..."
    echo ""

    AVAIL_OUTPUT="$(dnf repoquery --available --queryformat '%{name}\n' "${UNIQUE_PKGS[@]}" 2>/dev/null | sort -u)"

    for pkg in "${UNIQUE_PKGS[@]}"; do
        if echo "${AVAIL_OUTPUT}" | grep -qx "${pkg}"; then
            echo "  PASS: ${pkg}"
            PASS_COUNT=$((PASS_COUNT + 1))
        else
            echo "  FAIL: ${pkg} — not found in repos"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    done
fi

echo ""

for manifest in "${MANIFEST_DIR}"/*.txt; do
    filename="$(basename "${manifest}")"
    skipped=""
    while IFS= read -r line; do
        line="$(echo "${line}" | sed 's/#.*//' | xargs)"
        [[ -z "${line}" ]] && continue
        if [[ "${line}" == linta-* ]] || [[ "${line}" == lintactl ]]; then
            skipped="${skipped} ${line}"
        fi
    done < "${manifest}"
    if [[ -n "${skipped}" ]]; then
        echo "  SKIP (custom in ${filename}):${skipped}"
    fi
done

echo ""
echo "================================="
echo "Results: ${PASS_COUNT} passed, ${SKIP_COUNT} skipped (custom), ${FAIL_COUNT} failed"

if [[ ${FAIL_COUNT} -gt 0 ]]; then
    echo "VALIDATION FAILED: ${FAIL_COUNT} package(s) not found in Fedora repos."
    exit 1
else
    echo "All packages validated."
    exit 0
fi
