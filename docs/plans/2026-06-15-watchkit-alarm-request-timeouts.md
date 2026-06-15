# WatchKit Alarm Request Timeouts

Status: Planned

## Context

The dedicated alarm submission manager inherits `NSURLSessionConfiguration`
defaults for request and resource timeouts. A stalled endpoint can therefore
retain the watch request for a platform-defined duration rather than the
repository owning a bounded submission contract.

## Requirements

- **R1:** Configure a 10-second request timeout before constructing the alarm
  manager.
- **R2:** Configure a 15-second resource timeout before constructing the alarm
  manager.
- **R3:** Preserve POST submission, endpoint validation, redirect rejection,
  normalized parameters, request replacement, completion identity,
  cancellation, deactivation, and generic failure logging.
- **R4:** Add mutation-sensitive SDK-free contracts for both timeout values,
  manager-construction ordering, documentation, and completed evidence.
- **R5:** Record Apple-platform validation limits truthfully.

## Implementation Units

### U1. Bound alarm submission duration

**Files:** `Alarm WatchKit Extension/InterfaceController.swift`

**Approach:** Define named request and resource timeout constants and apply
them to the dedicated session configuration before manager construction. Keep
all existing manager headers, redirect refusal, and request lifecycle behavior.

**Verification:** The portable checker proves both values and their ordering
relative to manager construction.

### U2. Preserve the timeout contract

**Files:** `scripts/check_alarm_contracts.py`, `README.md`, `SECURITY.md`,
`AGENTS.md`, `CHANGES.md`,
`docs/plans/2026-06-15-watchkit-alarm-request-timeouts.md`

**Approach:** Register source, ordering, documentation, and completed-plan
contracts in the existing dependency-free baseline.

**Verification:** Isolated mutations to either constant, either assignment,
construction ordering, documentation, or plan status are rejected.

## Scope Boundaries

- Do not add retries, change endpoint policy, alter response handling, update
  dependencies, or modify legacy Xcode project membership.
- Do not contact an alarm endpoint or claim simulator, device, or server
  behavior from Linux.
- Keep this work stacked on the isolated redirect-manager pull request.

## Verification Plan

- Run the focused portable contract checker.
- Run repository-root and external-directory `make check` with bounded
  commands.
- Run isolated hostile mutations for both timeouts, assignments, ordering,
  documentation, and completed-plan evidence.
- Run `git diff --check` and explicit artifact, conflict-marker, large-file,
  and likely-secret audits before commit.
