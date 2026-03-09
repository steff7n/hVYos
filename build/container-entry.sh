#!/bin/bash
set -euo pipefail

# Linta Builder — container entrypoint
# Dispatches build commands inside the Fedora build environment.

WORKSPACE="/workspace"
RPM_OUTPUT="${WORKSPACE}/build/output/rpms"
ISO_OUTPUT="${WORKSPACE}/build/output/iso"
REPO_DIR="${WORKSPACE}/build/output/repo"

cmd_help() {
    echo "Linta Builder"
    echo "============="
    echo ""
    echo "Commands:"
    echo "  build-rpm <package>     Build a single Linta package RPM"
    echo "  build-rpm-all           Build all custom Linta RPMs"
    echo "  build-upstream <name>   Build an upstream package (niri, helix, etc.)"
    echo "  build-iso <profile>     Build an ISO (bare, kde, niri, combined)"
    echo "  create-repo             Generate local YUM repo from built RPMs"
    echo "  test                    Run all Python unit tests"
    echo "  validate                Validate package manifests"
    echo "  shell                   Drop into a bash shell"
    echo ""
    echo "Usage:"
    echo "  podman run --rm -v ./:/workspace:z linta-builder build-rpm lintactl"
    echo "  podman run --rm -v ./:/workspace:z linta-builder build-rpm-all"
    echo "  podman run --rm --privileged -v ./:/workspace:z linta-builder build-iso kde"
}

cmd_build_rpm() {
    local pkg="$1"
    local pkg_dir="${WORKSPACE}/packages/${pkg}"
    local spec

    spec=$(find "${pkg_dir}" -name '*.spec' -print -quit 2>/dev/null)
    if [[ -z "${spec}" ]]; then
        echo "Error: no spec file found in packages/${pkg}/"
        exit 1
    fi

    echo "Building RPM: ${pkg}"
    mkdir -p "${RPM_OUTPUT}"

    local name version
    name=$(rpmspec -q --qf '%{NAME}' "${spec}" 2>/dev/null | head -1)
    version=$(rpmspec -q --qf '%{VERSION}' "${spec}" 2>/dev/null | head -1)

    local tarball="${name}-${version}.tar.gz"
    tar czf "${HOME}/rpmbuild/SOURCES/${tarball}" \
        -C "${WORKSPACE}/packages" "${pkg}" \
        --transform="s|^${pkg}|${name}-${version}|"

    rpmbuild -ba "${spec}" 2>&1

    find "${HOME}/rpmbuild/RPMS" -name '*.rpm' -exec cp {} "${RPM_OUTPUT}/" \;
    find "${HOME}/rpmbuild/SRPMS" -name '*.rpm' -exec cp {} "${RPM_OUTPUT}/" \;

    echo "Done: ${pkg} -> ${RPM_OUTPUT}/"
}

cmd_build_rpm_all() {
    local packages=(lintactl linta-snapshots linta-nvidia linta-welcome
                    linta-flatpak-manager linta-keybindings)

    echo "Building all Linta RPMs..."
    echo ""

    local built=0 failed=0
    for pkg in "${packages[@]}"; do
        echo "════════════════════════════════"
        if cmd_build_rpm "${pkg}" 2>&1; then
            built=$((built + 1))
        else
            echo "FAILED: ${pkg}"
            failed=$((failed + 1))
        fi
        echo ""
    done

    echo "════════════════════════════════"
    echo "Results: ${built} built, ${failed} failed"

    if [[ ${failed} -gt 0 ]]; then
        exit 1
    fi
}

cmd_build_upstream() {
    local name="$1"
    local spec="${WORKSPACE}/build/packages/specs/${name}.spec"

    if [[ ! -f "${spec}" ]]; then
        echo "Error: spec not found: ${spec}"
        echo "Available: $(ls "${WORKSPACE}/build/packages/specs/"*.spec 2>/dev/null | xargs -I{} basename {} .spec | tr '\n' ' ')"
        exit 1
    fi

    echo "Building upstream package: ${name}"
    mkdir -p "${RPM_OUTPUT}"

    spectool -g -R "${spec}" 2>&1 || {
        echo "Warning: spectool could not download source. Provide it manually in ~/rpmbuild/SOURCES/"
    }

    rpmbuild -ba "${spec}" 2>&1

    find "${HOME}/rpmbuild/RPMS" -name '*.rpm' -exec cp {} "${RPM_OUTPUT}/" \;
    echo "Done: ${name} -> ${RPM_OUTPUT}/"
}

cmd_create_repo() {
    echo "Creating local Linta repo..."
    mkdir -p "${REPO_DIR}"

    if ls "${RPM_OUTPUT}"/*.rpm &>/dev/null; then
        cp "${RPM_OUTPUT}"/*.rpm "${REPO_DIR}/"
    fi

    createrepo_c "${REPO_DIR}"
    echo "Repo created at ${REPO_DIR}/"
    echo ""
    echo "To use in a kickstart, add:"
    echo "  repo --name=linta --baseurl=file://${REPO_DIR}/"
}

cmd_build_iso() {
    local profile="${1:-kde}"
    local ks="${WORKSPACE}/build/kickstart/linta-${profile}.ks"

    if [[ ! -f "${ks}" ]]; then
        echo "Error: kickstart not found: ${ks}"
        exit 1
    fi

    echo "Building ISO: ${profile}"
    mkdir -p "${ISO_OUTPUT}"

    local flat_ks
    flat_ks="$(mktemp)"
    ksflatten -c "${ks}" -o "${flat_ks}" --version F42
    sed -i 's|\$releasever|42|g' "${flat_ks}"

    # Add local Linta repo if it exists
    if [[ -d "${REPO_DIR}" ]] && ls "${REPO_DIR}"/*.rpm &>/dev/null; then
        sed -i "/^url /a repo --name=linta-local --baseurl=file://${REPO_DIR}/ --cost=100" "${flat_ks}"
    fi

    local timestamp
    timestamp="$(date +%Y%m%d)"
    local iso_name="linta-${profile}-42-x86_64-${timestamp}.iso"

    livemedia-creator \
        --ks="${flat_ks}" \
        --no-virt \
        --resultdir="${ISO_OUTPUT}" \
        --project="Linta" \
        --releasever="42" \
        --volid="Linta-${profile}" \
        --iso-only \
        --iso-name="${iso_name}" \
        2>&1 | tee "${ISO_OUTPUT}/build-${profile}.log"

    rm -f "${flat_ks}"

    if [[ -f "${ISO_OUTPUT}/${iso_name}" ]]; then
        local size sha
        size=$(du -h "${ISO_OUTPUT}/${iso_name}" | cut -f1)
        sha=$(sha256sum "${ISO_OUTPUT}/${iso_name}" | cut -d' ' -f1)
        echo "${sha}  ${iso_name}" > "${ISO_OUTPUT}/${iso_name}.sha256"

        echo ""
        echo "ISO built successfully:"
        echo "  File:   ${ISO_OUTPUT}/${iso_name}"
        echo "  Size:   ${size}"
        echo "  SHA256: ${sha}"
    else
        echo "Error: ISO was not created."
        exit 1
    fi
}

cmd_test() {
    echo "Running Linta unit tests..."
    cd "${WORKSPACE}"

    local total=0 passed=0 failed=0
    for test_dir in packages/lintactl packages/linta-snapshots packages/linta-nvidia; do
        local name
        name=$(basename "${test_dir}")
        echo ""
        echo "── ${name} ──"

        test_file=$(find "${test_dir}" -name 'test_*.py' -print -quit)
        if [[ -n "${test_file}" ]]; then
            if (cd "${test_dir}" && python3 -m pytest "$(basename "${test_file}")" -v 2>/dev/null) || \
               (cd "${test_dir}" && python3 -m unittest "$(basename "${test_file}" .py)" -v 2>&1); then
                ((passed++))
            else
                ((failed++))
            fi
        fi
        ((total++))
    done

    echo ""
    echo "Results: ${passed}/${total} test suites passed"
    [[ ${failed} -gt 0 ]] && exit 1 || true
}

cmd_validate() {
    cd "${WORKSPACE}"
    bash build/testing/validate-manifests.sh
    echo ""
    bash build/testing/validate-kickstarts.sh
}

# Dispatch
case "${1:-help}" in
    build-rpm)      shift; cmd_build_rpm "$@" ;;
    build-rpm-all)  cmd_build_rpm_all ;;
    build-upstream) shift; cmd_build_upstream "$@" ;;
    build-iso)      shift; cmd_build_iso "$@" ;;
    create-repo)    cmd_create_repo ;;
    test)           cmd_test ;;
    validate)       cmd_validate ;;
    shell)          exec /bin/bash ;;
    help|--help|-h) cmd_help ;;
    *)              exec "$@" ;;
esac
