#!/bin/bash
set -euo pipefail

# Linta Linux — Master test runner
# Runs all available validation and test scripts.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TESTING_DIR="${PROJECT_ROOT}/build/testing"

TOTAL=0
PASSED=0
FAILED=0

run_test() {
    local name="$1"
    local script="$2"
    ((TOTAL += 1))

    echo ""
    echo "[$TOTAL] ${name}"
    echo "────────────────────────────────"

    if [[ ! -x "${script}" ]]; then
        echo "  SKIP: script not found or not executable"
        return
    fi

    if "${script}"; then
        ((PASSED += 1))
        echo "  ✓ PASSED"
    else
        ((FAILED += 1))
        echo "  ✗ FAILED"
    fi
}

echo "Linta Linux — Test Suite"
echo "========================"

run_test "Package manifest validation" "${TESTING_DIR}/validate-manifests.sh"
run_test "Kickstart file validation" "${TESTING_DIR}/validate-kickstarts.sh"

echo ""
echo "========================"
echo "Results: ${PASSED}/${TOTAL} passed, ${FAILED} failed"

if [[ ${FAILED} -gt 0 ]]; then
    exit 1
fi
