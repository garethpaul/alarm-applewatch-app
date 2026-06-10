# WatchKit CI Baseline

Status: Completed

## Goal

Enforce the repository's dependency-free static contracts on every pull request
and push to `master` without presenting a Linux job as an Apple build.

## Requirements

- CI runs the same lint and static contract commands available locally.
- CI uses read-only repository permissions, a bounded timeout, and a pinned
  checkout and Python setup actions.
- CI runs the checker on Python 3.10, 3.12, and 3.14 and supports manual
  maintenance dispatch.
- The automation target does not succeed by skipping an unavailable Xcode build.
- Documentation distinguishes deterministic CI from Xcode build and simulator
  validation.

## Implementation

- Add `make ci` as the shared lint and contract-test target.
- Add `.github/workflows/check.yml` on Ubuntu for the deterministic checks.
- Extend `scripts/check_alarm_contracts.py` to verify the CI safety contract.
- Document the CI and Apple-toolchain verification boundary in `README.md`.

## Verification

- `make ci`
- `make check`
- `git diff --check`

An Xcode build remains required on macOS before claiming WatchKit runtime or
simulator compatibility.
