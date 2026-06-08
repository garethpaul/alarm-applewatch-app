---
title: Alarm WatchKit Static Contract Coverage
status: completed
date: 2026-06-08
origin: user-requested continuous engineering quality loop
execution: code
---

# Alarm WatchKit Static Contract Coverage

## Problem Frame

The endpoint contract pass made `make check` useful on machines without Xcode,
but the check still focused mostly on the alarm URL boundary. This legacy sample
also depends on fragile WatchKit plist links, a simulator notification payload,
Xcode target metadata, and old CocoaPods dependency pins.

## Scope Boundaries

- Preserve the current Swift behavior and configured HTTPS placeholder.
- Do not migrate Alamofire, CocoaPods, Swift, WatchKit APIs, or project files.
- Keep static checks as a baseline, not a replacement for Xcode verification.

## Implementation Units

### U1: Broaden Static Contracts

Files:

- `scripts/check_alarm_contracts.py`

Approach:

- Parse app, WatchKit app, WatchKit extension, and test plists.
- Confirm the WatchKit extension points at the WatchKit app bundle.
- Confirm App Transport Security arbitrary loads are not enabled.
- Parse `PushNotificationPayload.apns` as JSON and validate its category/action.
- Confirm Xcode target product types and CocoaPods pins remain explicit.

### U2: Document the Quality Gate

Files:

- `README.md`
- `CHANGES.md`

Approach:

- Describe the specific contracts covered by `make check`.
- Record the expanded static coverage in the change log.

## Verification

- `make check`
- `git diff --check`
