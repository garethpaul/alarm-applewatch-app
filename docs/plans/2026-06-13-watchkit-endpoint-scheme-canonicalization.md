---
title: WatchKit Endpoint Scheme Canonicalization
date: 2026-06-13
type: implementation-plan
---

# WatchKit Endpoint Scheme Canonicalization

Status: Planned

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

## Planned Verification

- Local and external-working-directory `make check`
- Hosted Python 3.10, 3.12, and 3.14 static contracts when available
- Hostile mutations for raw-prefix restoration, missing canonicalization,
  plaintext acceptance, predicate bypass, documentation, and plan status
- Exact diff, generated-artifact, secret-pattern, conflict, and whitespace audit
