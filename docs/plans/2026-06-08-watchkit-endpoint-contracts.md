---
title: Alarm WatchKit Endpoint Contracts
status: completed
date: 2026-06-08
origin: user-requested continuous engineering quality loop
execution: code
---

# Alarm WatchKit Endpoint Contracts

## Problem Frame

The WatchKit extension sends alarm requests to a hardcoded plain HTTP endpoint.
The project vision calls out endpoint configuration and HTTPS transport as the
next safety boundary for this legacy sample.

## Scope Boundaries

- Preserve the single alarm-time request behavior.
- Do not migrate Swift, WatchKit, CocoaPods, Alamofire, or project settings.
- Do not add credentials or production alarm-service claims.
- Use static checks when Xcode is unavailable.

## Implementation Units

### U1: Static Endpoint Contracts

Files:

- Create `scripts/check_alarm_contracts.py`
- Create `Makefile`
- Create `CHANGES.md`

Approach:

- Check that the alarm endpoint is plist-backed, HTTPS-only, and documented.

### U2: Configure Endpoint Boundary

Files:

- Modify `Alarm WatchKit Extension/InterfaceController.swift`
- Modify `Alarm WatchKit Extension/Info.plist`
- Modify `README.md`

Approach:

- Read `AlarmEndpointURL` from the extension plist.
- Skip the network request when the endpoint is missing or not HTTPS.
- Document the placeholder endpoint and `make check` flow.

## Verification

- `make check`
- `git diff --check`
