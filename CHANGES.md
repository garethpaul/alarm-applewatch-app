# Changes

## 2026-06-08

- Added static contracts for the WatchKit alarm endpoint, HTTPS transport expectation, and workspace wiring.
- Added `make check` as the local verification entry point when Xcode is unavailable.
- Expanded the static contracts to cover WatchKit plist links, notification
  payload JSON, Xcode target types, and legacy CocoaPods pins.
- Added source-level alarm-hour normalization so the WatchKit request path
  mirrors the storyboard's 5 through 11 slider range.
