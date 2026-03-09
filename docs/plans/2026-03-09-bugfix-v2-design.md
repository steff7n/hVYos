# Bugfix V2 Design

## Goal

Fix the confirmed bugs from the deep bug-hunt, starting with installer and build pipeline failures, while keeping a running user-facing log in `bug_report_v2.md`.

## Scope

This pass starts with the highest-impact path:

1. Broken top-level and container test runners
2. Broken build configuration for mock and ISO generation
3. Installer flow and metadata correctness
4. Runtime/package/theme mismatches found during the review

## Approach

Work in small regression-proof slices:

1. Add or extend a focused test that demonstrates the bug
2. Run the targeted test and confirm it fails for the expected reason
3. Implement the smallest fix that resolves the failure
4. Re-run the targeted test, then broader verification
5. Append the finding, fix, and verification result to `bug_report_v2.md`

For shell/config regressions that are hard to execute directly in the current environment, use repo-local regression tests that validate the expected behavior or configuration contract.

## Design Decisions

### Build entrypoints first

The repo's own validation/test entrypoints are currently unreliable, so they must be fixed before leaning on them for later verification. This includes:

- `scripts/run-tests.sh`
- `build/container-entry.sh`

### Keep the container and standalone ISO flows aligned

The container entrypoint and `scripts/build-iso.sh` should use the same ISO builder family and output expectations. Divergent implementations create hidden failures and misleading docs.

### Make installer behavior explicit and testable

The installer currently mixes user interaction, install decisions, and on-disk configuration in a way that hides important bugs. The fix pass will add tests around the main control flow and extract small helpers only when needed to make the behavior testable.

### Log all fixes in one place

`bug_report_v2.md` is the running audit trail for:

- confirmed findings
- planned fix order
- per-fix notes
- verification evidence

## Testing Strategy

- Add focused Python regression tests for shell entrypoints where feasible
- Add installer unit tests for navigation and configuration helpers
- Re-run targeted tests after each slice
- Re-run `pytest -q` and `make test` at the end
- Re-run `bash scripts/run-tests.sh` after the runner fix to prove the script itself works
