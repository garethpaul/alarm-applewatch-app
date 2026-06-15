# WatchKit Ephemeral Alarm Session

Status: In Progress

## Context

Alarm submissions use a dedicated `Alamofire.Manager`, but its underlying
`NSURLSessionConfiguration` is the persistent default configuration. A one-shot
alarm POST does not need durable cookies, credentials, or response cache state,
and retaining that session data creates avoidable cross-launch privacy and
behavioral coupling.

## Priorities

1. **P0: Use an ephemeral alarm session.** Keep alarm request state isolated
   from persistent cookie, credential, and cache stores.
2. **P1 follow-up: Bound unused response bodies.** Revisit only with a proven
   Alamofire 1.2-compatible streaming or cancellation path that preserves
   completion semantics.
3. **P2 follow-up: Modernize networking.** Replace pinned Alamofire and legacy
   Swift only as a coordinated Apple-platform compatibility effort.

This plan implements only P0.

## Requirements

- Build the dedicated alarm manager from an ephemeral session configuration.
- Preserve Alamofire default HTTP headers, the 10-second request timeout, the
  15-second resource timeout, redirect refusal, and manager-before-request
  ordering.
- Preserve POST submission, normalized `alarmTime`, endpoint validation,
  current-request identity, cancellation, completion cleanup, and deactivation.
- Add mutation-sensitive source, ordering, documentation, and completed-plan
  contracts to the portable checker.

## Scope Boundaries

- Do not change endpoint rules, request parameters, response validation,
  dependencies, Xcode project settings, signing, retry behavior, or UI.
- Do not claim Xcode, simulator, device, or live-endpoint behavior without
  execution evidence.

## Implementation Units

### U1: Make the dedicated manager ephemeral

**Files:** `Alarm WatchKit Extension/InterfaceController.swift`

**Approach:** Replace the persistent default configuration with Foundation's
ephemeral configuration while retaining the existing header, timeout, manager,
and redirect-hook sequence.

**Verification:** Source-order contracts prove ephemeral configuration and all
existing privacy, timeout, redirect, and request lifecycle guards coexist.

### U2: Keep portable evidence and guidance synchronized

**Files:** `scripts/check_alarm_contracts.py`, `README.md`, `SECURITY.md`,
`AGENTS.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-15-watchkit-ephemeral-alarm-session.md`

**Approach:** Register the ephemeral manager contract, maintained privacy
guidance, and completed-plan evidence in the SDK-free checker.

**Verification:** Isolated mutations to configuration type, ordering,
documentation, and plan completion are rejected.

## Verification Plan

- Run the focused portable checker and Python compilation.
- Run every documented Make gate from the repository and the complete check
  through the absolute Makefile path from an external directory.
- Run isolated hostile mutations for source, ordering, guidance, and plan
  evidence.
- Audit exact intended paths, generated artifacts, conflict markers,
  credential-shaped additions, and whitespace before committing.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and validation.
