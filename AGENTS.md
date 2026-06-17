# AGENTS.md

## Repository purpose

`garethpaul/alarm-applewatch-app` is an Apple platform application or Swift sample. AppleWatch Alarm App

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `Podfile` - CocoaPods dependency definition
- `Alarm.xcodeproj` - Xcode project
- `Alarm.xcworkspace` - Xcode workspace
- `Alarm` - repository source or sample assets
- `Alarm WatchKit App` - repository source or sample assets
- `Alarm WatchKit Extension` - repository source or sample assets
- `AlarmTests` - repository source or sample assets

## Development commands

- Install dependencies: `pod install`
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- Local Apple development: `open Alarm.xcworkspace`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Swift (5).
- Use the CocoaPods workspace when present; update `Podfile.lock` only with an intentional dependency change.
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- Test-related files detected: `AlarmTests/AlarmTests.swift`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- The WatchKit extension reads `AlarmEndpointURL` from `Alarm WatchKit Extension/Info.plist`. Keep local or production endpoints HTTPS-only, parseable with a host, scoped to the `/alarm` path, and free of embedded credentials, query strings, or fragments.
- The checked-in `AlarmEndpointURL` must remain on `example.invalid`; runtime
  validation rejects that inert placeholder until a real HTTPS `/alarm` endpoint
  is configured locally.
- The WatchKit alarm slider and request code clamp alarm hours to the 5 through
  11 range before integer conversion, displaying, or sending `alarmTime`;
  non-finite programmatic values fall back safely.
- WatchKit outlets are optional and label updates use optional chaining so a disconnected legacy storyboard outlet does not crash the controller.
- The WatchKit controller retains only the active request, cancels replaced
  submissions, and cancels outstanding work when the interface deactivates.
- Preserve the bounded alarm request and resource timeouts when changing the
  dedicated submission manager.
- Alarm submissions use an ephemeral session so cookies, credentials, and cache data are not persisted.
- Alarm submissions disable cookie, credential, and cache stores so one request cannot influence the next.
- Alarm endpoint validation checks both the HTTPS text prefix and the parsed `NSURL.scheme` before sending a request.
- Alarm endpoint validation checks the parsed URL path before sending a request, so host-only endpoints do not receive alarm submissions.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
