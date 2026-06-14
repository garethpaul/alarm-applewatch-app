# WatchKit Device Verification

Run this matrix on the exact reviewed commit with a compatible historical Xcode
and CocoaPods toolchain. Open `Alarm.xcworkspace`; repository static checks do
not substitute for simulator or paired-device evidence.

## Evidence Header

Record these values without endpoint credentials, alarm selections, account
data, device identifiers, or private response bodies:

- commit SHA and pull request
- tester and UTC timestamp
- macOS, Xcode, Swift, CocoaPods, and simulator runtime versions
- iPhone and Watch simulator pair or physical device models and OS versions
- clean install or upgrade path
- `xcodebuild` command, destination, and result

Mark each scenario `pass`, `fail`, `blocked`, or `not run`. Explain every
blocked or unexecuted row and keep screenshots, logs, and build products outside
git. Do not convert `not run` into passing evidence.

## Build And Launch

| Scenario | Expected result | Result | Evidence |
| --- | --- | --- | --- |
| Build `Alarm.xcworkspace` | Companion, WatchKit app, extension, and tests compile. | not run | |
| Fresh companion launch | The iPhone app starts without a crash. | not run | |
| Watch app activation | Storyboard outlets load and the interface becomes usable. | not run | |
| Watch app deactivation | Any active alarm request is cancelled and released. | not run | |
| Reactivation | No stale completion updates the new interface state. | not run | |

## Endpoint And Alarm Matrix

Use only an authorized HTTPS test endpoint with the exact `/alarm` path. Supply
configuration outside git; the checked-in `example.invalid` value must remain
inert.

| Scenario | Expected result | Result | Evidence |
| --- | --- | --- | --- |
| Placeholder endpoint | Submission fails closed before network dispatch. | not run | |
| Valid alarm hour | One POST carries the bounded alarm parameter. | not run | |
| Repeated submission | The prior request is cancelled before the next starts. | not run | |
| Deactivate during request | Completion cannot update the inactive interface. | not run | |
| Redirect response | No follow-up request is transmitted. | not run | |
| Non-2xx response | Current request clears and one generic failure is logged. | not run | |
| Transport failure | UI remains usable and dependency details are not logged. | not run | |

Sanitized logs must not contain the endpoint URL, alarm time, credentials,
response body, dependency exception details, or device identifiers.

## Notification Matrix

1. Load `Alarm WatchKit Extension/PushNotificationPayload.apns` in the Watch
   simulator and verify the notification controller renders without a crash.
2. Exercise foreground and background delivery where the selected toolchain
   supports it.
3. Confirm notification evidence contains no production account or device data.

## Completion

Record the final result, unresolved failures, and protected evidence links. A
runtime claim requires all applicable rows to pass on the exact commit. This
repository currently records every simulator and physical-device row as
unexecuted.
