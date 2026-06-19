# WatchKit Alarm Session Storage Isolation

Status: Completed

## Problem

Alarm submissions use a dedicated ephemeral `NSURLSessionConfiguration`, which
prevents cookies, credentials, and cache data from being written to disk.
Apple's session documentation also states that ephemeral session data remains
in RAM until the session is invalidated, and its default cache is a private
in-memory cache. Because `alarmRequestManager` is a process-wide singleton,
state received by one alarm submission can influence later submissions during
the same extension lifetime.

Primary sources:

- https://developer.apple.com/documentation/foundation/urlsessionconfiguration/1410529-ephemeral
- https://developer.apple.com/documentation/foundation/urlsessionconfiguration/urlcache

## Priorities

1. P0: Prevent alarm submissions from retaining or reusing HTTP cookies,
   credentials, and cached responses across requests.
2. P1: Preserve the dedicated ephemeral manager, bounded timeouts, redirect
   refusal, POST submission, response validation, and request lifecycle.
3. P1: Add mutation-sensitive portable evidence without claiming unavailable
   native WatchKit execution.

## Requirements

1. The alarm manager must continue to start from
   `ephemeralSessionConfiguration()`.
2. Its configuration must explicitly disable cookie acceptance/sending,
   cookie storage, credential storage, and URL caching before manager creation.
   The legacy Swift properties are `HTTPShouldSetCookies`, `HTTPCookieStorage`,
   `URLCredentialStorage`, and `URLCache`.
3. Alamofire default headers, the 10-second request timeout, the 15-second
   resource timeout, and the isolated redirect delegate must remain unchanged.
4. Endpoint validation, POST parameters, current-request identity,
   cancellation, completion cleanup, failure redaction, and deactivation must
   remain unchanged.
5. No process-wide Alamofire manager or shared Foundation store may be mutated.
6. Dependencies, project settings, signing, endpoint configuration, retries,
   and UI behavior must not change.
7. The portable checker, maintained guidance, changelog, and this plan must
   preserve completed implementation and truthful verification evidence.

## Implementation Units

### U1: Disable Per-Session State Stores

**File:** `Alarm WatchKit Extension/InterfaceController.swift`

Configure the existing ephemeral session with no cookie store, no credential
store, no URL cache, and cookie handling disabled before constructing the
dedicated Alamofire manager. Keep the current initialization ordering and
manager ownership.

### U2: Add Durable Contracts

**Files:** `scripts/check_alarm_contracts.py`, `README.md`, `SECURITY.md`,
`AGENTS.md`, `VISION.md`, `CHANGES.md`, and this plan.

Require each storage boundary, source ordering, unchanged transport and
lifecycle behavior, maintained guidance, completed plan status, and actual
verification evidence. Reject isolated mutations that restore any store,
re-enable cookies, move configuration after manager construction, weaken
guidance, or falsify completion.

## Test Scenarios

- The dedicated manager still uses an ephemeral configuration.
- Cookie handling is disabled and no cookie store is attached.
- No credential store or URL cache is attached.
- All state-store settings occur before `Manager(configuration:)`.
- Existing request headers, timeouts, redirect refusal, POST behavior,
  response validation, replacement cancellation, completion identity, and
  deactivation contracts remain green.
- Repository and external-directory gates pass.

## Scope Boundaries

- Do not create one manager per request or change connection reuse.
- Do not mutate `Manager.sharedInstance` or Foundation shared stores.
- Do not modernize Alamofire, Swift, CocoaPods, Xcode project settings, or the
  endpoint in this change.
- Do not add retries, authentication, response-body parsing, or UI state.
- Native Xcode, simulator, paired-device, and live-endpoint validation remain
  outside this Linux environment and must not be claimed.

## Verification

- Run the focused portable checker before and after implementation.
- Run every maintained Make gate from the repository and `make check`
  from an external directory with explicit timeouts.
- Reject isolated hostile mutations for all four storage settings, ordering,
  existing transport/lifecycle behavior, guidance, and plan completion.
- Audit exact paths, generated artifacts, dependency/project/workflow drift,
  credentials, conflict markers, file modes, large files, and whitespace
  before commit.

## Completed Verification

- Apple Foundation documentation confirmed that ephemeral session data is
  retained in RAM until invalidation and that the default ephemeral URL cache
  is an in-memory cache.
- The portable checker failed before implementation on the missing storage,
  guidance, and completed-plan contracts.
- `make lint`, `make test`, `make ci`, `make verify`, and `make check` passed
  from the repository; external-directory `make check` passed through the
  absolute Makefile path.
- Eight isolated hostile mutations were rejected across the ephemeral
  baseline, cookie handling, cookie storage, credential storage, URL cache,
  initialization ordering, maintained guidance, and plan completion.
- Exact-path, generated-artifact, dependency/project/workflow drift,
  credential, conflict-marker, file-mode, large-file, and whitespace audits
  are recorded by the final validation pass.
- Xcode, simulator, paired-device, and live-endpoint validation were not run
  because this Linux host does not provide Apple tooling or an authorized
  endpoint.
