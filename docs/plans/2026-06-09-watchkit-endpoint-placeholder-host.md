# WatchKit Endpoint Placeholder Host

## Status: Completed

## Context

The WatchKit extension now reads `AlarmEndpointURL` from its checked-in
`Info.plist` and validates that URL before sending alarm requests. The static
checker rejected the old `myhome.com` endpoint and validated HTTPS URL shape,
but it did not require the committed placeholder to remain non-production.

## Objectives

- Preserve the existing plist-backed endpoint configuration path.
- Keep real alarm service hosts out of committed source.
- Require the checked-in placeholder host to remain `example.com`.
- Keep all existing HTTPS, path, credential, query, and fragment checks.
- Cover the placeholder-host rule in the SDK-free static checker.

## Work Completed

- Added a static checker assertion that `AlarmEndpointURL` stays on
  `example.com` in the checked-in extension plist.
- Added plan completion coverage for the placeholder-host rule.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_alarm_contracts.py`
- `make check`
- `git diff --check`
