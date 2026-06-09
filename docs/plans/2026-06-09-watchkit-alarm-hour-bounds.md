---
title: WatchKit Alarm Hour Bounds
type: reliability
status: completed
date: 2026-06-09
---

# WatchKit Alarm Hour Bounds

## Problem Frame

The WatchKit storyboard constrains the alarm slider to hours 5 through 11, but
`InterfaceController` trusts the incoming slider value and sends the stored
`wakeUp` value directly as the `alarmTime` request parameter. Programmatic calls
or future storyboard edits can bypass that implicit UI contract.

## Scope Boundaries

- Preserve the existing `alarmTime` parameter name.
- Preserve the existing Alamofire GET request and configured endpoint behavior.
- Do not change WatchKit UI layout, CocoaPods, Xcode project settings, or
  notification behavior in this pass.

## Implementation Units

### U1: Mirror Slider Bounds In Source

Files:

- Modify `Alarm WatchKit Extension/InterfaceController.swift`

Approach:

- Add named minimum and maximum alarm-hour constants that match the storyboard.
- Normalize slider values and stored alarm values through a single helper.
- Use the normalized value for display text and request parameters.

### U2: Extend Static Contracts

Files:

- Modify `scripts/check_alarm_contracts.py`

Approach:

- Verify that the storyboard keeps the 5 through 11 slider range.
- Verify that `InterfaceController` normalizes alarm values before display and
  before request parameter construction.

### U3: Document The Bound

Files:

- Modify `README.md`
- Modify `CHANGES.md`
- Modify `VISION.md`

Approach:

- Record the maintained alarm-hour range in the repo docs and changelog.

## Verification

- `make check`
- `git diff --check`

Xcode build verification remains dependent on an Apple toolchain with the
matching legacy WatchKit support.
