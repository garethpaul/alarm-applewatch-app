# Changes

## 2026-06-15

- Alarm submissions use an ephemeral session so cookies, credentials, and cache data are not persisted.
- Bounded alarm submissions with explicit request and resource timeouts on the
  dedicated WatchKit session manager.
- Scoped alarm redirect refusal to a dedicated Alamofire manager so submitting
  an alarm cannot change redirect behavior for unrelated shared-manager
  requests.

## 2026-06-14

- Rejected alarm endpoint configuration with an explicit port so validated
  requests stay on the default HTTPS origin.
- Validated alarm responses, released the still-current request on completion,
  and logged failures without endpoint, alarm-time, response, or dependency
  details.
- Added mutation-sensitive completion, stale-callback, documentation, and plan
  contracts.
- Rejected alarm redirect follow-up requests through Alamofire's pinned session
  delegate before another target can receive the POST.
- Added an exact-commit WatchKit simulator and paired-device verification matrix
  for launch, alarm requests, lifecycle cancellation, failures, notifications,
  and privacy-safe evidence, with every runtime row explicitly unexecuted.

## 2026-06-13

- Made parsed HTTPS scheme validation case-insensitive and removed the raw
  lowercase-prefix gate while preserving every endpoint boundary.
- Made the reserved alarm placeholder comparison case-insensitive and
  independent of a trailing root dot.
- Extended static contracts and security guidance for DNS-equivalent
  `example.invalid` forms.
- Changed the state-changing alarm submission from GET to POST so `alarmTime`
  is not encoded into request URLs.
- Added portable method, documentation, and completed-plan contracts.
- Rejected the full `example.invalid` placeholder subdomain namespace while
  preserving unrelated hostname near matches.
- Added mutation-sensitive contracts and guidance for placeholder subdomains.

## 2026-06-12

- Guarded WatchKit alarm-hour float conversion so `NaN`, infinities, and
  extreme programmatic values clamp before reaching `Int` conversion.
- Added static contracts and a completed plan for the safe conversion order.
- Bound the single disabled checkout credential setting to the checkout action
  so moving or overriding it cannot satisfy the CI safety contract.

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
