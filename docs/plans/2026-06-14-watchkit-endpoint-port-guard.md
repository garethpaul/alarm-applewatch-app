# WatchKit Endpoint Port Guard

Status: Planned

## Problem

`alarmEndpointURL()` requires HTTPS, the exact `/alarm` path, and no embedded
credentials, query, fragment, placeholder host, or redirect. It still accepts
an explicit port, which allows configuration to select a different origin than
the reviewed default HTTPS endpoint.

## Requirements

1. Reject `AlarmEndpointURL` values with any explicit port before creating an
   Alamofire request.
2. Preserve trimming, parsing, HTTPS, host, path, placeholder-host, credential,
   query, fragment, POST, parameter, redirect, and request-lifecycle behavior.
3. Add a fail-closed static contract and maintained guidance for the port
   boundary.
4. Record only verification that actually runs on the current environment and
   leave native WatchKit compilation to the hosted baseline.

## Scope Boundaries

- Do not change endpoint configuration ownership or add a real service URL.
- Do not modernize Swift, WatchKit, Alamofire, CocoaPods, or project settings.
- Do not change request method, alarm parameters, retries, response handling,
  redirect policy, or controller lifecycle behavior.
- Do not merge or close stacked pull requests without explicit authorization.

## Implementation

1. Require the parsed endpoint port to be absent in `alarmEndpointURL()`.
2. Extend the portable source checker with both positive and bypass-rejection
   contracts scoped to endpoint validation.
3. Update security and configuration guidance to state the default-port-only
   boundary.

## Verification

- Python syntax and focused portable contract checks.
- Repository-root and external-directory `make check`.
- Isolated hostile mutations for port inspection, rejection, bypass, guidance,
  and completed-plan evidence.
- Exact diff, generated-artifact, changed-line secret, and whitespace audits.
- One bounded exact-head hosted snapshot after push; no polling or wait loop.

## Risks

- Linux cannot compile or execute the legacy WatchKit target; the hosted Xcode
  baseline remains authoritative for Swift compatibility.
- Private deployments that intentionally use a nondefault HTTPS port must move
  behind a standard-port endpoint before adopting this stricter contract.
