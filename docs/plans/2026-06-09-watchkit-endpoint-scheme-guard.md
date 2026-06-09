# WatchKit Endpoint Scheme Guard

## Status: Completed

## Context

`alarmEndpointURL()` required configured endpoints to start with `https://`
before parsing them as `NSURL` values. The parsed URL fields are already used
for host, credential, query, and fragment checks, so the parsed scheme should
also be checked explicitly before the extension sends an alarm request.

## Objectives

- Preserve the existing endpoint configuration path.
- Keep the text-prefix HTTPS guard for legacy readability.
- Require the parsed `NSURL.scheme` to equal `https`.
- Keep host, credential, query, and fragment rejection unchanged.
- Extend static checker coverage for parsed scheme validation.

## Work Completed

- Added a parsed `url.scheme` optional binding in `alarmEndpointURL()`.
- Required the parsed scheme to equal `https` before returning the endpoint.
- Extended `scripts/check_alarm_contracts.py`.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_alarm_contracts.py`
- `make check`
- `git diff --check`

On this workspace, `make check` reported `xcodebuild unavailable; skipping
legacy Apple build`.

## Follow-Up Candidates

- Add focused Swift/XCTest coverage for endpoint parsing in an Apple toolchain.
- Consider a documented path allowlist if the alarm service endpoint stabilizes.
