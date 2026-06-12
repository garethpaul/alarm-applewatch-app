# WatchKit Non-Finite Alarm Hour Guard

Status: Completed

## Context

The WatchKit slider normally emits values between 5 and 11, but
`normalizedAlarmHour(value: Float)` converts its input to `Int` before applying
the existing bounds. Non-finite or extreme programmatic values can therefore
trap during conversion instead of falling back to a valid alarm hour.

## Changes

- Detect `NaN` without converting it and fall back to the minimum alarm hour.
- Clamp values below or above the supported range while they are still floats.
- Convert to `Int` only after the input is known to be finite and in range.
- Preserve the 5 through 11 slider, display, request parameter, endpoint, and
  request lifecycle contracts.
- Extend the dependency-free checker and project documentation with the safe
  conversion requirements.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- Static mutation checks for pre-conversion `NaN` and range guards
- `git diff --check`

An Xcode build remains required on macOS before claiming runtime compatibility
with the legacy Swift and WatchKit toolchain.
