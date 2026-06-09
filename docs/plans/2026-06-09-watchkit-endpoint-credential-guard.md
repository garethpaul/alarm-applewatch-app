---
title: WatchKit Endpoint Credential Guard
type: security
status: completed
date: 2026-06-09
---

# WatchKit Endpoint Credential Guard

## Problem Frame

`AlarmEndpointURL` is configuration, not a credential store. The endpoint
validation already required HTTPS and a host, but a URL such as
`https://user:password@example.com/alarm` would still parse and could place
sensitive values in source-controlled plist files, logs, crash reports, or
network debugging output.

## Scope Boundaries

- Preserve the plist-backed endpoint configuration.
- Preserve the existing Alamofire request path and `alarmTime` parameter.
- Do not introduce authentication behavior in this legacy WatchKit sample.
- Keep verification available on hosts without Xcode.

## Implementation Units

### U1: Reject Credential-Bearing URLs

Files:

- Modify `Alarm WatchKit Extension/InterfaceController.swift`

Approach:

- Continue trimming and parsing `AlarmEndpointURL`.
- Return a configured endpoint only when it is HTTPS, has a host, and has no
  username or password component.

### U2: Cover The Guard

Files:

- Modify `scripts/check_alarm_contracts.py`

Approach:

- Require the Swift endpoint validator to check both `url.user` and
  `url.password`.
- Require the checked-in plist placeholder to remain credential-free.

### U3: Document The Maintenance Rule

Files:

- Modify `README.md`
- Modify `VISION.md`
- Modify `CHANGES.md`

Approach:

- Record that endpoint configuration must not embed credentials.
- Keep any future authentication work separate and explicit.

## Verification

- `python3 scripts/check_alarm_contracts.py`
- `make check`
- `git diff --check`

`make check` attempts an Xcode build when `xcodebuild` is present; on hosts
without Xcode, the SDK-free static contracts remain the baseline verification.
