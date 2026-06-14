# WatchKit Alarm Redirect Rejection

Status: Completed

## Context

The alarm endpoint is validated as an explicit HTTPS `/alarm` URL before the
request starts, but Alamofire 1.2.1 follows HTTP redirects by default. A server
or intermediary can therefore move the POST to another target after the local
endpoint checks have passed.

## Scope

- Configure Alamofire’s shared session delegate to reject redirects before the
  alarm request starts.
- Preserve endpoint validation, POST parameters, response validation, request
  ownership, stale-callback suppression, logging, and deactivation cleanup.
- Add mutation-sensitive portable contracts for the redirect hook, nil return,
  configuration order, documentation, and completed plan evidence.
- Document the fixed-target transport boundary and pinned-library API source.

## Implementation Units

### 1. Reject redirects before submission

Files:

- `Alarm WatchKit Extension/InterfaceController.swift`

Install the Alamofire 1.2.1 task redirect closure and return `nil` before
creating the POST request.

### 2. Protect the contract

Files:

- `scripts/check_alarm_contracts.py`
- `docs/plans/2026-06-14-watchkit-alarm-redirect-rejection.md`

Require the exact hook, cancellation result, ordering, and completed plan
evidence in the SDK-free checker.

### 3. Document the behavior

Files:

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Describe redirects as rejected before follow-up transmission.

## Verification

Completed on 2026-06-14:

- The portable checker recognized the redirect hook, nil return, configuration
  order, and documentation, failing only while this plan was intentionally
  incomplete.
- The pinned Alamofire 1.2.1 tagged source confirms the public redirect closure
  accepts a nullable follow-up request and passes its result to the URL session
  completion handler.
- No Swift compiler, Xcode, watchOS SDK, or simulator is installed on the Linux
  host; the repository's `make check` gate is the applicable local validation.
- Full `make check` passed the portable contract suite and truthfully skipped
  the unavailable legacy Apple build.
- Five focused mutations were rejected when they removed the hook, returned the
  redirect request, moved configuration after request creation, removed the
  security wording, or changed this plan back to `Status: Planned`.

## Risks

- Any legitimate endpoint redirect will now fail through the existing generic
  alarm submission failure path and requires updating `AlarmEndpointURL`.
- The redirect hook is global to Alamofire’s shared manager within the WatchKit
  extension; this project has only the alarm request on that manager.
- Xcode and a watchOS simulator may remain unavailable on the Linux host.

## Reference

- Alamofire 1.2.1 `SessionDelegate.taskWillPerformHTTPRedirection` source:
  https://github.com/Alamofire/Alamofire/blob/1.2.1/Source/Alamofire.swift
