# Linta Linux — Testing Infrastructure

## Validation Scripts

| Script | Purpose | Dependencies |
|---|---|---|
| `validate-manifests.sh` | Check all packages in manifests exist in Fedora repos | `dnf` |
| `validate-kickstarts.sh` | Validate kickstart syntax with ksvalidator | `pykickstart` |
| `test-iso-boot.sh` | Boot ISO in QEMU and verify it starts | `qemu-system-x86-core` |

## Running Tests

From the project root:

```bash
./scripts/run-tests.sh          # Run all validation tests
./build/testing/test-iso-boot.sh <path-to.iso>  # Test a specific ISO
```

## CI Integration

These scripts are designed to be called from any CI system (GitHub Actions,
GitLab CI, Jenkins, etc.). Each exits with 0 on success, non-zero on failure.

The automated testing gate (openQA or custom) is an open item — these scripts
provide the foundation for whatever CI system is chosen.
