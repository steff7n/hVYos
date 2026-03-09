#!/bin/bash
set -euo pipefail

# Linta Linux — Kickstart file validator
# Validates syntax of all kickstart files and checks package/group names
# against Fedora repositories.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KS_DIR="${SCRIPT_DIR}/../kickstart"
RELEASEVER="${RELEASEVER:-42}"
UPSTREAM_SPECS_DIR="${SCRIPT_DIR}/../packages/specs"
SYNTAX_FAIL=0
REPO_FAIL=0
REPO_PASS=0
GROUP_FAIL=0
GROUP_PASS=0
PKG_FAIL=0
PKG_PASS=0
PKG_SKIP=0

ALL_GROUPS=()
ALL_PKGS=()
declare -A GROUP_OWNERS
declare -A PKG_OWNERS

echo "Linta Kickstart Validator"
echo "========================="
echo ""

if ! command -v ksvalidator &>/dev/null; then
    echo "Error: ksvalidator not found. Install pykickstart:"
    echo "  dnf install pykickstart"
    exit 1
fi

if ! command -v ksflatten &>/dev/null; then
    echo "Error: ksflatten not found. Install pykickstart:"
    echo "  dnf install pykickstart"
    exit 1
fi

if ! command -v dnf &>/dev/null; then
    echo "Error: dnf not found."
    exit 1
fi

append_owner() {
    local current="$1"
    local filename="$2"

    if [[ " ${current} " == *" ${filename} "* ]]; then
        printf '%s' "${current}"
    elif [[ -n "${current}" ]]; then
        printf '%s %s' "${current}" "${filename}"
    else
        printf '%s' "${filename}"
    fi
}

for ks in "${KS_DIR}"/linta-*.ks; do
    filename="$(basename "${ks}")"
    echo -n "  ${filename}: "

    if [[ "${filename}" == "linta-base.ks" ]]; then
        echo "SKIP (partial — included by profile kickstarts)"
        continue
    fi

    tmpfile="$(mktemp)"
    if ! ksflatten -c "${ks}" -o "${tmpfile}" --version "F${RELEASEVER}" 2>/dev/null; then
        echo "FAIL (ksflatten error)"
        SYNTAX_FAIL=$((SYNTAX_FAIL + 1))
        rm -f "${tmpfile}"
        continue
    fi

    if ksvalidator "${tmpfile}" 2>/dev/null; then
        echo "PASS"
    else
        echo "WARN (validation issues, may be non-fatal)"
    fi

    mapfile -t repo_names < <(python3 - "${tmpfile}" <<'PY'
import sys
from imgcreate import kickstart as imgkickstart
from pykickstart.parser import KickstartParser
from pykickstart.version import makeVersion

ks = KickstartParser(makeVersion("F42"))
ks.readKickstart(sys.argv[1])
imgkickstart.convert_method_to_repo(ks)
for repo in imgkickstart.get_repos(ks):
    print(repo[0])
PY
    )

    missing_repo=0
    for required_repo in fedora updates; do
        if [[ " ${repo_names[*]} " != *" ${required_repo} "* ]]; then
            echo "  FAIL: missing repo '${required_repo}' after kickstart flatten (${filename})"
            REPO_FAIL=$((REPO_FAIL + 1))
            missing_repo=1
        fi
    done
    if [[ ${missing_repo} -eq 0 ]]; then
        REPO_PASS=$((REPO_PASS + 1))
    fi

    in_packages=0
    while IFS= read -r raw_line; do
        line="$(printf '%s' "${raw_line%%#*}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

        if [[ "${line}" == %packages* ]]; then
            in_packages=1
            continue
        fi

        if [[ ${in_packages} -eq 1 && "${line}" == "%end" ]]; then
            in_packages=0
            continue
        fi

        [[ ${in_packages} -eq 0 || -z "${line}" ]] && continue
        [[ "${line}" == -* ]] && continue

        if [[ "${line}" == @* ]]; then
            group="${line#@}"
            ALL_GROUPS+=("${group}")
            GROUP_OWNERS["${group}"]="$(append_owner "${GROUP_OWNERS[${group}]-}" "${filename}")"
            continue
        fi

        if [[ "${line}" == linta-* ]] || [[ "${line}" == lintactl ]] || [[ -f "${UPSTREAM_SPECS_DIR}/${line}.spec" ]]; then
            PKG_SKIP=$((PKG_SKIP + 1))
            continue
        fi

        ALL_PKGS+=("${line}")
        PKG_OWNERS["${line}"]="$(append_owner "${PKG_OWNERS[${line}]-}" "${filename}")"
    done < "${tmpfile}"

    rm -f "${tmpfile}"
done

echo ""

echo "Kickstart repo checks: ${REPO_PASS} passed, ${REPO_FAIL} failed"
echo ""

if [[ ${#ALL_GROUPS[@]} -gt 0 ]]; then
    UNIQUE_GROUPS=($(printf '%s\n' "${ALL_GROUPS[@]}" | sort -u))

    echo "Checking ${#UNIQUE_GROUPS[@]} kickstart groups against Fedora repos..."
    for group in "${UNIQUE_GROUPS[@]}"; do
        if dnf group info "${group}" &>/dev/null; then
            GROUP_PASS=$((GROUP_PASS + 1))
        else
            echo "  FAIL: @${group} — not found in repos (${GROUP_OWNERS[${group}]})"
            GROUP_FAIL=$((GROUP_FAIL + 1))
        fi
    done
    echo "  Groups: ${GROUP_PASS} passed, ${GROUP_FAIL} failed"
    echo ""
fi

if [[ ${#ALL_PKGS[@]} -gt 0 ]]; then
    UNIQUE_PKGS=($(printf '%s\n' "${ALL_PKGS[@]}" | sort -u))
    AVAILABLE_OUTPUT="$(dnf repoquery --available --queryformat '%{name}\n' "${UNIQUE_PKGS[@]}" 2>/dev/null | sort -u)"

    declare -A AVAILABLE_PKGS=()
    while IFS= read -r pkg; do
        [[ -n "${pkg}" ]] && AVAILABLE_PKGS["${pkg}"]=1
    done <<< "${AVAILABLE_OUTPUT}"

    echo "Checking ${#UNIQUE_PKGS[@]} kickstart packages against Fedora repos..."
    for pkg in "${UNIQUE_PKGS[@]}"; do
        if [[ -n "${AVAILABLE_PKGS[${pkg}]+x}" ]]; then
            PKG_PASS=$((PKG_PASS + 1))
        else
            echo "  FAIL: ${pkg} — not found in repos (${PKG_OWNERS[${pkg}]})"
            PKG_FAIL=$((PKG_FAIL + 1))
        fi
    done
    echo "  Packages: ${PKG_PASS} passed, ${PKG_SKIP} skipped (custom/local), ${PKG_FAIL} failed"
    echo ""
fi

TOTAL_FAIL=$((SYNTAX_FAIL + REPO_FAIL + GROUP_FAIL + PKG_FAIL))
if [[ ${TOTAL_FAIL} -gt 0 ]]; then
    echo "FAILED: ${TOTAL_FAIL} kickstart issue(s) found."
    exit 1
else
    echo "All kickstart files validated."
fi
