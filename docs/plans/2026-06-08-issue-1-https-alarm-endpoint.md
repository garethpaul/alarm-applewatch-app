---
title: Issue 1 HTTPS Alarm Endpoint
type: fix
status: active
date: 2026-06-08
origin: https://github.com/garethpaul/alarm-applewatch-app/issues/1
execution: code
---

# Issue 1 HTTPS Alarm Endpoint

## Summary

Move the WatchKit alarm request off the hardcoded plain-HTTP endpoint so the sample no longer sends alarm updates over cleartext transport.

## Problem Frame

Issue #1 was filed from the public repository review because `Alarm WatchKit Extension/InterfaceController.swift` sends a runtime Alamofire request to `http://myhome.com/alarm`. The app is a legacy WatchKit sample, and this workspace cannot compile it without Xcode and the historical CocoaPods toolchain, so the change should stay narrow and source-reviewable.

## Requirements

- R1. `Alarm WatchKit Extension/InterfaceController.swift` must not contain a runtime `http://myhome.com/alarm` endpoint.
- R2. The alarm request must continue to use the existing `alarmTime` parameter and `wakeUp` value.
- R3. The README must no longer describe the alarm endpoint as plain HTTP in its current-state notes.
- R4. The change must avoid Swift, Alamofire, CocoaPods, or Xcode project migrations.
- R5. The PR must reference `https://github.com/garethpaul/alarm-applewatch-app/issues/1`.

## Implementation Unit

### U1. HTTPS Alarm Endpoint

- **Goal:** Change the default alarm endpoint constant from HTTP to HTTPS and update README modernization notes to describe endpoint configuration as future hardening rather than the current cleartext flaw.
- **Files:** `Alarm WatchKit Extension/InterfaceController.swift`, `README.md`
- **Test Scenarios:** Verify no `http://myhome.com/alarm` runtime endpoint remains, `setAlarm()` still sends `alarmTime: String(wakeUp)`, and only source/docs files changed.
- **Verification:** `rg -n "http://myhome\\.com/alarm|https://myhome\\.com/alarm|alarmTimeParameter|Alamofire.request" "Alarm WatchKit Extension/InterfaceController.swift" README.md` and `git diff --check`.

## Risks

- This workspace does not provide `xcodebuild` or CocoaPods, so compile and simulator verification are unavailable locally.
- The sample still uses a placeholder `myhome.com` endpoint. A later pass should move the endpoint to a build setting or runtime configuration once the project can be compiled with the intended Apple toolchain.
