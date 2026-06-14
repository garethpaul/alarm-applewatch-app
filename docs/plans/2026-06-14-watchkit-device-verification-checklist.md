# WatchKit Device Verification Checklist

Status: In Progress

## Problem

Portable contracts cover the legacy WatchKit project and alarm request path,
but no checklist defines the simulator or paired-device evidence required before
claiming runtime behavior.

## Requirements

1. Add an exact-commit matrix for companion launch, WatchKit activation,
   alarm-hour submission, request lifecycle, failures, and notifications.
2. Require toolchain, simulator/device, endpoint, result, and sanitized evidence.
3. Keep repository checks separate from unexecuted Apple runtime scenarios.
4. Add mutation-sensitive contracts for the checklist and completion evidence.

## Scope Boundaries

- Do not modernize Swift, Xcode project format, CocoaPods, Alamofire, or WatchKit.
- Do not add a real endpoint, credentials, build products, logs, or device data.
- Do not claim Xcode, simulator, or physical-device execution from Linux checks.
- Do not merge or close stacked pull requests without explicit authorization.

## Verification

- Pending implementation and bounded repository validation.
