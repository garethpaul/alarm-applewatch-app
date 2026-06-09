# alarm-applewatch-app

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/alarm-applewatch-app` is an Apple platform application or Swift sample. AppleWatch Alarm App

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Swift (5).

## Repository Contents

- `README.md` - project overview and local usage notes
- `Podfile` - Apple platform dependency metadata
- `Alarm` - source or example code
- `Alarm WatchKit App` - source or example code
- `Alarm WatchKit Extension` - source or example code
- `Alarm.xcodeproj` - Xcode project file
- `AlarmTests` - source or example code
- `docs` - source or example code
- `Podfile.lock` - Apple platform dependency metadata
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: Alarm, Alarm WatchKit App, Alarm WatchKit Extension, AlarmTests, docs
- Dependency and build manifests: Podfile, Podfile.lock
- Entry points or build surfaces: Alarm.xcodeproj
- Test-looking files: AlarmTests/AlarmTests.swift, AlarmTests/Info.plist

## Getting Started

### Prerequisites

- Git
- macOS with Xcode for building Apple platform projects
- CocoaPods if dependencies need to be installed

### Setup

```bash
git clone https://github.com/garethpaul/alarm-applewatch-app.git
cd alarm-applewatch-app
pod install
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Open `Alarm.xcworkspace` in Xcode, choose the app or sample scheme, and run it on the matching simulator/device.

## Testing and Verification

- `make check` - runs dependency-free static contracts and attempts an Xcode build when `xcodebuild` is available
- Xcode's test action or `xcodebuild test` with the appropriate scheme and destination

The static contracts cover endpoint configuration, WatchKit plist relationships,
notification payload JSON, Xcode target types, and legacy CocoaPods pins. When
the required SDK or runtime is unavailable, use static checks and source review
first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- The WatchKit extension reads `AlarmEndpointURL` from `Alarm WatchKit Extension/Info.plist`. Keep local or production endpoints HTTPS-only, parseable with a host, and free of committed credentials.
- The WatchKit alarm slider and request code clamp alarm hours to the 5 through 11 range before displaying or sending `alarmTime`.
- WatchKit outlets are optional and label updates use optional chaining so a disconnected legacy storyboard outlet does not crash the controller.

## Security and Privacy Notes

- Review changes touching network requests, sockets, or service endpoints; examples from the scan include Alarm/Info.plist, Alarm WatchKit App/Info.plist, Alarm WatchKit Extension/Info.plist, Alarm WatchKit Extension/InterfaceController.swift, and 3 more.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include Alarm/Info.plist, Alarm WatchKit App/Info.plist, Alarm WatchKit Extension/Info.plist, AlarmTests/Info.plist.
- Review changes touching database, model, or persistence code; examples from the scan include docs/plans/2026-06-08-watchkit-maintainability-baseline.md.

## Maintenance Notes

- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- See `CHANGES.md` and `docs/plans/2026-06-08-watchkit-endpoint-contracts.md`
  for the current endpoint configuration baseline.
- See `docs/plans/2026-06-09-watchkit-alarm-hour-bounds.md` for the
  alarm-hour bounds contract.
- See `docs/plans/2026-06-09-watchkit-outlet-safety.md` for the nil-safe
  outlet contract.
- See `docs/plans/2026-06-09-watchkit-endpoint-url-shape.md` for the
  parseable endpoint URL contract.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
