# WatchKit Isolated Redirect Manager

Status: Planned

## Context

The alarm request rejects redirects by assigning a closure to
`Manager.sharedInstance.delegate.taskWillPerformHTTPRedirection`. In pinned
Alamofire 1.2.1 that closure belongs to the shared session delegate, so one
alarm submission permanently changes redirect behavior for every unrelated
request using the global manager. The same version supports a dedicated
`Manager` with its own session delegate.

## Requirements

- **R1:** Keep redirect refusal scoped to alarm submissions rather than the
  process-wide Alamofire shared manager.
- **R2:** Preserve Alamofire's default session configuration and HTTP headers.
- **R3:** Preserve POST submission, normalized parameters, request replacement,
  validation, completion identity, cancellation, and deactivation behavior.
- **R4:** Add SDK-free contracts that reject shared-manager mutation, use of the
  top-level request helper, missing redirect refusal, or incomplete evidence.
- **R5:** Document actual local, mutation, hosted, and Apple-platform limits.

## Implementation Units

1. Add one private alarm request manager configured with Alamofire default
   headers and redirect refusal on its own delegate.
2. Route the existing alarm POST through that dedicated manager and remove the
   shared delegate mutation from `setAlarm()`.
3. Extend `AlarmTests/AlarmTests.swift` fixtures and
   `scripts/check_alarm_contracts.py` with mutation-sensitive manager-isolation
   contracts.
4. Update `README.md`, `SECURITY.md`, `CHANGES.md`, and this plan with the
   completed boundary and truthful verification.

## Test Scenarios

- The alarm manager owns the redirect-refusal closure before requests exist.
- Alarm submission uses the dedicated manager exactly once.
- `Manager.sharedInstance` and top-level `Alamofire.request` are absent from
  alarm request creation.
- Existing endpoint and request lifecycle contracts remain green.

## Scope Boundaries

- Do not change the endpoint, alarm parameter, request method, dependencies,
  retry behavior, response handling, or legacy project settings.
- Do not add a live endpoint or claim simulator, device, or server behavior on
  Linux.
- Keep this work stacked on the endpoint-port guard pull request.

## Verification To Complete

- Run focused Python contract checks and the complete root/external `make check`.
- Reject isolated mutations covering shared-manager use, top-level request use,
  missing default headers, missing redirect refusal, documentation, and plan
  completion.
- Run exact diff, generated-artifact, and likely-secret audits.
- Take one bounded exact-head hosted snapshot after push without polling.
