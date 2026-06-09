# WatchKit Endpoint Path Guard

## Status: Completed

## Context

The WatchKit endpoint validator required a trimmed HTTPS URL with a host and
rejected credentials, query strings, and fragments. A host-only endpoint such as
`https://example.com` could still pass validation and receive alarm submissions
at the service root rather than the intended alarm route.

## Objectives

- Preserve plist-backed `AlarmEndpointURL` configuration.
- Preserve the existing Alamofire request and `alarmTime` parameter.
- Require parsed endpoint URLs to use the explicit `/alarm` path.
- Keep SDK-free static verification available without Xcode.

## Work Completed

- Added an `alarmEndpointPath` constant in `InterfaceController.swift`.
- Required `alarmEndpointURL()` to inspect `url.path` and match `/alarm`
  before returning a configured endpoint.
- Extended the static contract checker for source and plist placeholder path
  validation.
- Updated README, VISION, SECURITY, and CHANGES.

## Verification

- Red: `make test` failed on the missing endpoint path contract.
- Green: `make test` passes after adding the parsed path guard.
- Full gate: `make check`.
