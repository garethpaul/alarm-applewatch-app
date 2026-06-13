# WatchKit Placeholder Domain Suffix

Status: Planned

## Context

The alarm endpoint validator rejects the exact reserved host
`example.invalid`, including case and trailing-dot variants. A subdomain such
as `api.example.invalid` is part of the same reserved placeholder namespace but
currently passes validation and can start an Alamofire request that cannot
reach a real alarm service.

## Requirements

- Reject `example.invalid` and every canonical subdomain beneath it.
- Keep near matches such as `notexample.invalid` eligible when every other
  endpoint contract passes.
- Preserve canonical lowercase and trailing-root-dot handling.
- Preserve HTTPS, exact `/alarm` path, credential/query/fragment rejection,
  POST parameters, cancellation, and real-host behavior.
- Add mutation-sensitive SDK-free contracts and truthful verification evidence.

## Implementation Units

### U1: Classify Reserved Placeholder Hosts

**File:** `Alarm WatchKit Extension/InterfaceController.swift`

Add a small predicate over the canonical host that rejects either the exact
placeholder or a host ending in `.` plus the placeholder. Use the predicate in
the existing endpoint validator without rewriting returned production URLs.

### U2: Enforce The Boundary

**File:** `scripts/check_alarm_contracts.py`

Require exact-host and dot-delimited suffix rejection, use of the predicate in
endpoint validation, explicit near-match protection, and completed plan
evidence.

### U3: Document And Verify

**Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, this plan

Document the reserved-domain boundary. Run focused hostile mutations, full and
external SDK-free gates, diff/artifact/secret scans, and exact-head hosted
checks without claiming unavailable Xcode or device coverage.

## Scope Boundaries

- Do not change the endpoint plist, request method, parameters, dependencies,
  project settings, signing, UI, or alarm-hour behavior.
- Do not broaden this unit into general DNS, SSRF, or allowlist policy.
- Do not claim Xcode, simulator, signing, or device validation on Linux.

## Verification Plan

- Prove exact placeholder, subdomain suffix, delimiter, canonicalization, and
  predicate-use mutations fail the SDK-free checker.
- Run `make check` locally and from an isolated external directory.
- Run `git diff --check`, generated-artifact inspection, and added-line secret
  scans before committing implementation paths.
- Record hosted evidence only after querying the exact pushed head.

## Sources

- RFC 2606, Reserved Top Level DNS Names:
  https://www.rfc-editor.org/rfc/rfc2606
