# WatchKit Placeholder Host Canonicalization

Status: Completed

## Context

The checked-in alarm endpoint uses the reserved `example.invalid` host and the
runtime rejects that exact string before creating an Alamofire request. DNS
hostnames are case-insensitive and may include a trailing root dot, so equivalent
forms such as `EXAMPLE.INVALID` or `example.invalid.` should remain inert rather
than being treated as configured endpoints.

## Requirements

- **R1:** Compare the parsed alarm endpoint host in a lowercase, trailing-dot
  independent form.
- **R2:** Reject uppercase and fully qualified variants of the checked-in
  `example.invalid` placeholder.
- **R3:** Preserve HTTPS, path, credential, query, fragment, request lifecycle,
  alarm-hour, and real-host behavior.
- **R4:** Extend the SDK-free checker and documentation with the canonical host
  boundary.
- **R5:** Record truthful local, mutation, and hosted validation evidence.

## Implementation Units

### U1: Canonicalize The Placeholder Comparison

**File:** `Alarm WatchKit Extension/InterfaceController.swift`

Add a small host canonicalization helper and compare its result with the named
placeholder constant. Do not rewrite or return a canonicalized production URL.

### U2: Enforce The Runtime Contract

**File:** `scripts/check_alarm_contracts.py`

Require lowercase and trailing-dot normalization before the placeholder
comparison, and require this completed plan in the canonical inventory.

### U3: Document And Verify

**Files:** `README.md`, `SECURITY.md`, `CHANGES.md`, this plan

Document equivalent placeholder-host rejection and record focused, full,
mutation, external-directory, and hosted verification.

## Test Scenarios

- Removing lowercase normalization fails the SDK-free checker.
- Removing trailing-dot normalization fails the SDK-free checker.
- Comparing the raw host with `placeholderAlarmHost` fails the checker.
- Existing endpoint and request-lifecycle contracts remain green.

## Scope Boundaries

- Do not change the request method, parameters, endpoint path, plist value,
  dependencies, project settings, or signing configuration.
- Do not claim Xcode, simulator, or device validation on this Linux host.

## Verification

- The focused checker failed before implementation on missing host
  canonicalization and completed-plan evidence.
- Six hostile mutations were rejected: removing lowercase normalization,
  removing trailing-root-dot normalization, restoring the raw-host comparison,
  removing README guidance, removing security guidance, and removing this plan.
- `make lint` passed Python compilation. `make build` truthfully skipped because
  `xcodebuild` is unavailable on this Linux host.
- `make check` passed Python compilation and the SDK-free contract checker, and
  truthfully skipped the legacy Apple build because `xcodebuild` is unavailable.
- External-directory `make ci`, workflow YAML parsing, secret-pattern scanning,
  and `git diff --check` passed.
- Xcode, simulator, signing, and device behavior remain platform validation
  boundaries.

## Sources

- RFC 4343, Domain Name System Case Insensitivity Clarification:
  https://www.rfc-editor.org/rfc/rfc4343
- RFC 1034, Domain Names - Concepts and Facilities:
  https://www.rfc-editor.org/rfc/rfc1034
