# WatchKit Alarm Response Completion

Status: Planned

## Problem

The WatchKit controller retains the submitted Alamofire request but does not
validate or observe its response. Transport and non-2xx failures are silent,
and a completed request remains retained until another submission or interface
deactivation.

## Requirements

1. Validate submitted alarm responses with Alamofire's default 2xx contract.
2. Clear the retained request when the still-current request completes.
3. Ignore callbacks from cancelled or superseded requests so they cannot clear
   or report failure for a replacement request.
4. Log one stable generic failure category without endpoint, parameter,
   response, or dependency error details.
5. Preserve endpoint validation, POST parameters, cancellation ordering, and
   deactivation cleanup.
6. Add mutation-sensitive portable contracts and completed verification
   evidence.

## Implementation Units

### 1. Retain and observe one request identity

Create the POST request as a local identity, retain it, then attach validation
and a weak-controller completion closure. Handle completion only while that
same request is still current.

### 2. Normalize completion behavior

Clear the current request before inspecting its result. Log only a fixed alarm
submission failure message when Alamofire reports an error; successful
completion remains silent.

### 3. Protect and document the contract

Extend the portable checker with request-validation, weak capture, identity,
ordering, generic logging, documentation, required-plan, and completed-status
contracts. Update maintenance, security, vision, and change guidance.

## Verification

- Run the portable checker before and after implementation.
- Run bounded root and external `make check` gates.
- Reject focused mutations for validation, weak capture, identity protection,
  clear-before-log ordering, generic logging, documentation, plan status, and
  plan presence.
- Run Python compilation, plist/workspace/project parsing, `git diff --check`,
  and explicit secret and generated-artifact audits.

## Scope Boundaries

- Do not add UI state, retries, response-body parsing, dependency updates, or
  endpoint changes.
- Do not merge or close any pull request without explicit owner authorization.
