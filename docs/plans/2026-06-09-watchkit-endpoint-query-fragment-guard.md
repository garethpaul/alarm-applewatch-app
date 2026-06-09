# WatchKit Endpoint Query Fragment Guard

## Status: Completed

## Context

The WatchKit endpoint validator already requires a trimmed HTTPS URL with a
host and rejects embedded usernames or passwords. Query strings and fragments
are also unsuitable for checked-in endpoint configuration because they can carry
tokens, mode switches, or other request-specific values outside the explicit
`alarmTime` parameter path.

## Objectives

- Preserve plist-backed `AlarmEndpointURL` configuration.
- Preserve the existing Alamofire request and `alarmTime` parameter.
- Reject endpoint URLs that include query strings or fragments.
- Keep SDK-free static verification available without Xcode.

## Work Completed

- Added `url.query == nil` and `url.fragment == nil` checks to
  `alarmEndpointURL()`.
- Extended the static contract checker for source and plist placeholder
  query/fragment rejection.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_alarm_contracts.py`
- `python3 -m py_compile scripts/check_alarm_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`

On this workspace, `make build`, `make check`, and `make verify` reported
`xcodebuild unavailable; skipping legacy Apple build`.

## Follow-Up Candidates

- Add simulator verification notes for configured and missing endpoint flows.
- Move future authentication into explicit request headers or app configuration,
  not endpoint URL components.
