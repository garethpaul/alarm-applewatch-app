---
title: WatchKit Maintainability Baseline
type: chore
status: completed
date: 2026-06-08
---

# WatchKit Maintainability Baseline

## Summary

Create a safe maintainability baseline for the legacy Apple Watch alarm app by documenting the pinned toolchain, making the WatchKit alarm request intent easier to audit, and recording the larger migration work that needs an Xcode-capable environment.

---

## Problem Frame

The repository is a first-commit-era Swift and WatchKit project with CocoaPods 0.37-era dependencies and no README. Local verification is limited in this environment because `xcodebuild` and CocoaPods are not installed, so this pass should avoid broad Swift, project-file, or dependency migrations that cannot be compiled here.

---

## Requirements

- R1. The repository must document the legacy Xcode, CocoaPods, workspace, and verification expectations needed by future maintainers.
- R2. The WatchKit alarm request should expose its endpoint and parameter name as named constants instead of burying them inside the network call.
- R3. The plan must identify the hardcoded insecure HTTP endpoint and outdated Alamofire/CocoaPods stack as follow-up modernization risks.
- R4. Local verification must distinguish source-review checks from unavailable toolchain checks.
- R5. The change must avoid runtime behavior changes until an Xcode-capable verification environment is available.

---

## Key Technical Decisions

- **Keep source changes behavior-preserving:** Extract constants in `InterfaceController.swift` without changing the URL, request method, or parameter payload.
- **Do not edit the Xcode project file manually:** Adding new Swift files or test targets would require project-file changes that cannot be validated without Xcode.
- **Document the workspace path:** CocoaPods-based builds should use `Alarm.xcworkspace`, not the bare `.xcodeproj`.
- **Defer dependency migration:** Updating Alamofire 1.2.1 or CocoaPods-era project settings should happen with compile and simulator verification.

---

## Scope Boundaries

- This pass does not migrate Swift syntax, WatchKit APIs, CocoaPods, or Alamofire.
- This pass does not replace the HTTP alarm endpoint.
- This pass does not add new Xcode targets or project-file membership.
- This pass does not change the alarm request payload or UI behavior.

---

## Implementation Units

### U1. Document Legacy Build and Verification

- **Goal:** Make the repository understandable and runnable for a future maintainer with the right Apple toolchain.
- **Files:** `README.md`
- **Patterns:** Keep instructions short; call out `Alarm.xcworkspace`, CocoaPods, and local verification prerequisites.
- **Test Scenarios:**
  - README names `Alarm.xcworkspace` as the workspace to open/build.
  - README lists `pod install`, `xcodebuild -list`, and an app test command as verification paths.
  - README records that this environment cannot run those commands without `xcodebuild` and `pod`.
- **Verification:** Manual README review plus `command -v xcodebuild` and `command -v pod`

### U2. Name WatchKit Request Constants

- **Goal:** Make the alarm endpoint and request parameter easier to audit before a future networking migration.
- **Files:** `Alarm WatchKit Extension/InterfaceController.swift`
- **Patterns:** File-level constants near the imports; leave the Alamofire call shape unchanged.
- **Test Scenarios:**
  - `setAlarm()` still sends a GET request to the same endpoint.
  - `setAlarm()` still sends the wake-up value under the same `alarmTime` parameter name.
- **Verification:** Source review and `git diff --check`

---

## Risks & Dependencies

- The alarm endpoint is currently plain HTTP and hardcoded to `http://myhome.com/alarm`; moving it to HTTPS or configuration is a follow-up behavior change.
- Alamofire 1.2.1 and CocoaPods 0.37-era project settings are obsolete and should be modernized with Xcode and simulator coverage.
- Placeholder tests in `AlarmTests/AlarmTests.swift` do not cover app behavior; adding meaningful tests likely requires extracting pure logic and updating Xcode project membership.

---

## Sources / Research

- `Podfile` and `Podfile.lock` show Alamofire 1.2.1 and CocoaPods 0.37.0 beta-era dependency state.
- `Alarm WatchKit Extension/InterfaceController.swift` contains the alarm slider state and hardcoded Alamofire request.
- `AlarmTests/AlarmTests.swift` contains placeholder XCTest coverage.
- `command -v xcodebuild` and `command -v pod` both fail in this environment, so compile/test verification is unavailable locally.
