# Changes

## 2026-06-10

- Retain one WatchKit alarm request at a time, cancelling prior submissions and
  outstanding work when the interface deactivates.
- Make repository checks location-independent and pin CI to Ubuntu 24.04 with
  superseded-run cancellation.
- Add a least-privilege GitHub Actions workflow for the deterministic static
  contract checks on Python 3.10, 3.12, and 3.14.
- Add a dedicated `make ci` target so automation cannot silently pass by
  skipping an unavailable Xcode build.
- Move the checked-in alarm endpoint to `example.invalid` and reject that
  sentinel at runtime so an unconfigured build cannot submit alarm data.

## 2026-06-09

- Required the checked-in WatchKit alarm endpoint placeholder to stay on
  `example.com` so real alarm hosts remain local configuration.
- Added static checker coverage for the placeholder endpoint host.
- Required parsed WatchKit alarm endpoint URLs to use the explicit `/alarm`
  path before sending alarm requests.
- Added static checker coverage for endpoint path validation.
- Required the parsed WatchKit alarm endpoint scheme to be exactly HTTPS before
  sending alarm requests.
- Added static checker coverage for parsed endpoint scheme validation.
- Rejected WatchKit alarm endpoint URLs that include query strings or fragments.
- Rejected WatchKit alarm endpoint URLs that embed usernames or passwords
  before the extension can send an alarm request.
- Replaced implicitly unwrapped WatchKit outlets in the alarm interface
  controller with optional outlets and nil-safe label updates, with static
  contracts to keep disconnected storyboard outlets from crashing the sample.
- Required `AlarmEndpointURL` to parse as an HTTPS URL with a host before the
  WatchKit extension sends the alarm request.

## 2026-06-08

- Added static contracts for the WatchKit alarm endpoint, HTTPS transport expectation, and workspace wiring.
- Added `make check` as the local verification entry point when Xcode is unavailable.
- Expanded the static contracts to cover WatchKit plist links, notification
  payload JSON, Xcode target types, and legacy CocoaPods pins.
- Added source-level alarm-hour normalization so the WatchKit request path
  mirrors the storyboard's 5 through 11 slider range.
