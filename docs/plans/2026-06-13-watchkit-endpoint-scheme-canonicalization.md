---
title: WatchKit Endpoint Scheme Canonicalization
date: 2026-06-13
type: implementation-plan
---

# WatchKit Endpoint Scheme Canonicalization

Status: Completed

## Summary

Validate the parsed alarm endpoint scheme case-insensitively so valid
mixed-case HTTPS configuration is accepted without weakening the existing
HTTPS-only, host, path, credential, query, fragment, or placeholder guards.

## Problem Frame

`alarmEndpointURL()` currently requires the raw string to begin with the exact
lowercase text `https://` before parsing it. URI schemes are case-insensitive,
so a valid endpoint such as `HTTPS://alarm.example/alarm` is rejected before
the parsed scheme guard runs.

## Requirements

- R1. Remove the case-sensitive raw-prefix gate and validate only the parsed
  canonical scheme.
- R2. Accept lowercase, uppercase, and mixed-case HTTPS scheme values.
- R3. Continue rejecting HTTP and every non-HTTPS parsed scheme.
- R4. Preserve trimming, URL parsing, host, `/alarm` path, credential, query,
  fragment, placeholder-host, POST, parameter, and request-lifecycle guards.
- R5. Add mutation-sensitive static and Swift contracts for canonicalization,
  predicate use, plaintext rejection, documentation, and completed evidence.

## Scope Boundaries

- Do not change the checked-in inert endpoint, real deployment configuration,
  request method, parameters, retries, response handling, or UI.
- Do not modernize Swift, WatchKit, CocoaPods, Alamofire, signing, or targets.
- Do not claim Xcode, XCTest, simulator, or device behavior without execution.

## Work Completed

- Removed the raw case-sensitive `https://` prefix gate.
- Added a parsed-scheme canonicalizer and required its lowercase result to equal
  `https` before returning the endpoint.
- Preserved all host, path, credential, query, fragment, placeholder, POST,
  parameter, and request-lifecycle contracts.
- Extended project guidance and the static checker with mutation-sensitive
  canonicalization, predicate-use, plaintext, and completed-plan evidence.

## Verification Completed

- Local `make check`, local `make ci`, and external-working-directory
  `make ci` passed all SDK-free contracts; Xcode truthfully skipped because
  `xcodebuild` is unavailable on this Linux host.
- Hosted Python 3.10, 3.12, and 3.14 results are recorded separately in tracker
  evidence after push; this plan makes no pre-push hosted claim.
- Six hostile mutations for raw-prefix restoration, missing canonicalization,
  plaintext acceptance, predicate bypass, documentation, and plan status
  were rejected
- Exact diff, generated-artifact, secret-pattern, conflict, and whitespace audit
  passed
