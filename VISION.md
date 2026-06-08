## Alarm Apple Watch App Vision

Alarm Apple Watch App is a legacy Swift and WatchKit sample. The watch
extension lets a user choose an alarm hour and send that value to a configured
alarm endpoint.

The repository is valuable as a compact example of early WatchKit application
structure, CocoaPods-era dependency management, and watch-to-service request
flow. Project setup notes live in [`README.md`](README.md).

The goal is to keep the sample understandable, buildable in an appropriate
Apple toolchain, and safe enough for future modernization work.

The current focus is:

Priority:

- Preserve the working structure around `Alarm.xcworkspace`
- Keep CocoaPods and Alamofire setup documented for the legacy codebase
- Make the alarm endpoint behavior visible rather than hidden in source code
- Avoid changes that require unavailable Apple tooling without documenting them

Next priorities:

- Move the alarm endpoint into configuration
- Prefer HTTPS and documented transport expectations
- Update the Swift, WatchKit, CocoaPods, and Alamofire stack in a dedicated pass
- Replace placeholder tests with coverage around extracted app behavior

Contribution rules:

- One PR = one topic. Do not mix dependency migration, endpoint configuration,
  and UI behavior changes unless the migration requires it.
- Open and build `Alarm.xcworkspace`, not `Alarm.xcodeproj`.
- Run the relevant `xcodebuild` checks when an Apple toolchain is available.
- Document toolchain constraints when verification cannot be completed locally.

## Security

Alarm requests should not depend on hardcoded plain HTTP endpoints long term.
Endpoint configuration, transport security, and any future authentication need
to be explicit and kept out of committed secrets.

Do not add logging that exposes user-selected alarm data, endpoint credentials,
or device-specific identifiers.

## What We Will Not Merge (For Now)

- Large rewrites that discard the sample's educational structure without a
  migration note
- New network behavior that keeps sensitive endpoints hardcoded
- Dependency updates without workspace verification
- Production alarm-service claims that are not backed by app behavior and tests

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
