# WatchKit Inert Endpoint Placeholder

Status: Completed

## Context

The checked-in WatchKit configuration used `https://example.com/alarm` as its
non-production endpoint. `example.com` is reserved for documentation, but it is
still a resolvable host, and the controller treated the value as configured.
Pressing the alarm button in an unconfigured build could therefore send the
selected alarm hour to infrastructure outside the project.

## Changes

- Replace the checked-in host with the reserved non-resolving
  `example.invalid` namespace.
- Reject that exact sentinel in `alarmEndpointURL()` so the request path is
  skipped until maintainers provide a real endpoint locally.
- Extend the SDK-free contracts to require both the inert plist value and the
  runtime rejection.
- Document the configuration behavior in the current README and project
  guardrails.

## Verification

- `make check`
- Static mutations for the plist host and runtime sentinel rejection
- `git diff --check`

An Xcode build remains required on macOS before claiming compatibility with the
legacy Swift and WatchKit toolchain.
