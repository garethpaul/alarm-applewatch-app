---
title: WatchKit Outlet Safety
type: reliability
status: completed
date: 2026-06-09
---

# WatchKit Outlet Safety

## Problem Frame

`InterfaceController` used implicitly unwrapped WatchKit outlets for the slider
and alarm label. A disconnected or renamed storyboard outlet can therefore crash
the legacy controller when it updates the alarm text during launch or slider
changes.

## Scope Boundaries

- Preserve the existing WatchKit storyboard, alarm-hour behavior, and Alamofire
  request flow.
- Do not migrate Swift, WatchKit, CocoaPods, or Xcode project settings in this
  pass.
- Avoid introducing runtime behavior that requires Xcode verification on hosts
  where `xcodebuild` is unavailable.

## Implementation Units

### U1: Make Controller Outlets Optional

Files:

- Modify `Alarm WatchKit Extension/InterfaceController.swift`

Approach:

- Convert `slider` and `alarmValue` from implicitly unwrapped outlets to
  optional outlets.
- Use optional chaining for every alarm label text update.
- Leave the normalized alarm-hour and request-parameter helpers unchanged.

### U2: Add Static Contracts

Files:

- Modify `scripts/check_alarm_contracts.py`

Approach:

- Assert that WatchKit outlets are not implicitly unwrapped.
- Assert that all alarm label updates use optional chaining.
- Keep the existing alarm-hour and endpoint checks in the same SDK-free checker.

### U3: Document The Guardrail

Files:

- Modify `README.md`
- Modify `VISION.md`
- Modify `CHANGES.md`

Approach:

- Record the outlet-safety rule with the rest of the WatchKit maintenance
  guardrails.
- Keep future storyboard or Swift modernization separate from this crash
  prevention pass.

## Verification

- `make check`
- `git diff --check`

`make check` attempts an Xcode build when `xcodebuild` is present; on hosts
without Xcode, the SDK-free static contracts remain the baseline verification.
