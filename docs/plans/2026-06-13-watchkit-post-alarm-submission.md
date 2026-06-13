# WatchKit POST Alarm Submission

Status: Planned

## Context

The WatchKit controller sends the state-changing alarm submission with HTTP
GET. Alamofire therefore encodes `alarmTime` into the request URL, where proxy,
server, analytics, and diagnostic logs or caches can retain it. Endpoint
validation, parameter normalization, and request lifecycle handling are
already explicit and should remain unchanged.

## Requirements

- **R1:** Submit alarm changes with Alamofire's POST method instead of GET.
- **R2:** Preserve the validated HTTPS `/alarm` endpoint, normalized
  `alarmTime` parameter, request replacement, and deactivation cancellation.
- **R3:** Extend SDK-free contracts to reject GET submission or removal of the
  POST privacy boundary.
- **R4:** Document truthful local, mutation, hosted, and Apple-platform
  verification evidence.

## Implementation Units

### U1: Change The Submission Method

**File:** `Alarm WatchKit Extension/InterfaceController.swift`

Change only the Alamofire request method from `.GET` to `.POST`.

### U2: Enforce The Method Contract

**File:** `scripts/check_alarm_contracts.py`

Require the exact POST request and reject any GET request carrying alarm
parameters. Add this plan to the canonical plan inventory.

### U3: Document And Verify

**Files:** `README.md`, `SECURITY.md`, `CHANGES.md`,
`docs/plans/2026-06-13-watchkit-post-alarm-submission.md`

Record the URL-data minimization boundary and actual verification.

## Test Scenarios

- Restoring `.GET` fails the portable checker.
- Removing `.POST`, the normalized parameters, cancellation, guidance, or
  completed-plan status fails verification.
- Existing endpoint, numeric, outlet, lifecycle, workflow, and plist contracts
  remain green.

## Scope Boundaries

- Do not change the endpoint, parameter name/value, retries, response handling,
  authentication, dependencies, or legacy Swift/Alamofire versions.
- Do not claim server compatibility or Apple runtime validation without a
  configured endpoint and Xcode-capable host.

## Verification

Pending implementation and execution.
