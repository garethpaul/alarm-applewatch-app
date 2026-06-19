# WatchKit Device Verification Checklist

Status: Completed

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

- `python3 -m py_compile scripts/check_alarm_contracts.py` and the focused
  WatchKit contract checker passed.
- Repository-root and external-working-directory `make check` passed all
  portable contracts and truthfully skipped the unavailable Xcode build.
- Twelve hostile mutations were rejected for removing checklist, workspace,
  lifecycle, request, redirect, notification, privacy, unexecuted-result,
  documentation, or completed-plan evidence.
- No Xcode, simulator, or physical-device scenario was executed; every runtime
  matrix row remains truthfully marked `not run`.
