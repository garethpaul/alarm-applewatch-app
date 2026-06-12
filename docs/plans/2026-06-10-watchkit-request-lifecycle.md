# WatchKit Alarm Request Lifecycle

Status: Completed

## Goal

Bound the legacy WatchKit controller to one alarm submission at a time and stop
outstanding network work when the interface is no longer active.

## Requirements

- `InterfaceController` retains at most one Alamofire request.
- Starting an alarm submission cancels and releases any previous request.
- Deactivating the controller cancels and releases the outstanding request.
- The SDK-free checker prevents the lifecycle contract from regressing.
- Repository checks work from outside the checkout directory.
- Hosted static verification uses a fixed runner and cancels superseded runs.

## Implementation

- Store the current Alamofire `Request` on `InterfaceController`.
- Cancel and clear that request before replacement and in `didDeactivate()`.
- Extend `scripts/check_alarm_contracts.py` with request-lifecycle, rooted
  `Makefile`, and CI runner/concurrency assertions.
- Resolve paths from the `Makefile` location and pin GitHub Actions to Ubuntu
  24.04 with workflow concurrency.

## Verification

- `make ci`
- `make check`
- `make -f /absolute/path/to/Makefile ci` from outside the repository
- request-lifecycle mutation checks
- `git diff --check`

An Xcode build remains required on macOS before claiming runtime compatibility
with the legacy Swift, WatchKit, CocoaPods, and Alamofire toolchain.
