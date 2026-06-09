# WatchKit Endpoint URL Shape

## Status: Completed

## Context

`alarmEndpointURL()` already read `AlarmEndpointURL` from the WatchKit
extension plist, trimmed it, and required an `https://` prefix. That still
allowed values such as `https://` or malformed strings to pass the prefix check
and be handed to the network request path.

## Objectives

- Keep the endpoint configured through `Alarm WatchKit Extension/Info.plist`.
- Preserve the HTTPS-only transport expectation.
- Require the configured endpoint to parse as a URL with a host before
  Alamofire is called.
- Keep the behavior covered by SDK-free static contracts.

## Work Completed

- Added an `NSURL` parse and host check inside `alarmEndpointURL()`.
- Extended `scripts/check_alarm_contracts.py` to require the source-level parse
  and a plist placeholder with an HTTPS scheme and host.
- Updated README, VISION, and CHANGES notes for the endpoint-shape contract.

## Verification

- `make check`
- `git diff --check`

`xcodebuild` is unavailable on this Linux host, so `make check` runs the static
contracts and skips the legacy Apple build step here.
