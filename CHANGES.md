# Changes

## 2026-06-26 15:27 PDT - P1 - Reject special-use alarm endpoints

- Summary: rejected IANA special-use alarm endpoint namespaces that satisfied
  the previous public-DNS-shaped hostname check.
- Rejected IANA special-use alarm endpoint namespaces before request creation.
- Files: tightened the Foundation policy, moved native fixtures off reserved
  example domains, added portable/native tests, six hostile mutations, a
  completed plan, and synchronized repository guidance.
- Tests: the focused portable contract failed before implementation on missing
  `.alt`; Ruby 4.0.5 then passed Python syntax, the full parsed repository
  contract, portable policy tests, the complete mutation suite including six
  new suffix mutations, and root/external `make check`.
- Findings: `.alt`, `.arpa`, `.onion`, and reserved example domains are not
  production public DNS destinations but were previously accepted.
- Blockers: native Foundation tests and legacy workspace parsing require macOS;
  the Linux baseline correctly skipped those rows. The requested Codex review
  for PR #20 returned HTTP 401 and was skipped after one attempt as instructed.
- Next action: require PR #20's hosted macOS native policy gate and merge only
  the exact hosted-green head before verifying post-merge workflows.

## 2026-06-21

- Required every hosted checkout step to own its adjacent credential-isolation
  setting and added a native-job decoy mutation that the previous first-step
  contract accepted.
- Required the exact portable and native verification commands; removing native
  tests or injecting a credential-persistence command now fails closed.

## 2026-06-19

- Rejected private/local, numeric, IDN, reserved, and ambiguous alarm endpoint
  destinations through a shared Foundation-native policy.
- Validated final response URL, status, declared media type, and body length;
  discarded response bytes and cancelled transfers above 4096 bytes.
- Added native fake-network, structural, and mutation-sensitive tests plus a
  hosted macOS policy gate.
- Made the unsupported WatchKit 1 / Swift 1 build an explicit Xcode 6-era opt-in
  while keeping workspace parsing in the portable macOS baseline.

## 2026-06-17

- Alarm submissions disable cookie, credential, and cache stores so one request cannot influence the next.

## 2026-06-15

- Alarm submissions use an ephemeral session so cookies, credentials, and cache data are not persisted.
- Bounded alarm submissions with explicit request and resource timeouts on the
  dedicated WatchKit session manager.
- Scoped alarm redirect refusal to a dedicated Alamofire manager so submitting
  an alarm cannot change redirect behavior for unrelated shared-manager
  requests.

## 2026-06-14

- Rejected alarm endpoint configuration with an explicit port so validated
  requests stay on the default HTTPS origin.
- Validated alarm responses, released the still-current request on completion,
  and logged failures without endpoint, alarm-time, response, or dependency
  details.
- Added mutation-sensitive completion, stale-callback, documentation, and plan
  contracts.
- Rejected alarm redirect follow-up requests through Alamofire's pinned session
  delegate before another target can receive the POST.
- Added an exact-commit WatchKit simulator and paired-device verification matrix
  for launch, alarm requests, lifecycle cancellation, failures, notifications,
  and privacy-safe evidence, with every runtime row explicitly unexecuted.

## 2026-06-13

- Made parsed HTTPS scheme validation case-insensitive and removed the raw
  lowercase-prefix gate while preserving every endpoint boundary.
- Made the reserved alarm placeholder comparison case-insensitive and
  independent of a trailing root dot.
- Extended static contracts and security guidance for DNS-equivalent
  `example.invalid` forms.
- Changed the state-changing alarm submission from GET to POST so `alarmTime`
  is not encoded into request URLs.
- Added portable method, documentation, and completed-plan contracts.
- Rejected the full `example.invalid` placeholder subdomain namespace while
  preserving unrelated hostname near matches.
- Added mutation-sensitive contracts and guidance for placeholder subdomains.

## 2026-06-12

- Guarded WatchKit alarm-hour float conversion so `NaN`, infinities, and
  extreme programmatic values clamp before reaching `Int` conversion.
- Added static contracts and a completed plan for the safe conversion order.
- Bound the single disabled checkout credential setting to the checkout action
  so moving or overriding it cannot satisfy the CI safety contract.

## 2026-06-10

- Retain one WatchKit alarm request at a time, cancelling prior submissions and
  outstanding work when the interface deactivates.
- Make repository checks location-independent and pin CI to Ubuntu 24.04 with
  superseded-run cancellation.
- Add a least-privilege GitHub Actions workflow for the deterministic static
  contract checks on Python 3.10, 3.12, and 3.14.
- Add a dedicated `make ci` target so automation cannot silently pass by
  skipping an unavailable Xcode build.
- Move the checked-in alarm endpoint to `example.invalid` and reject that
  sentinel at runtime so an unconfigured build cannot submit alarm data.

## 2026-06-09

- Required the checked-in WatchKit alarm endpoint placeholder to stay on
  `example.com` so real alarm hosts remain local configuration.
- Added static checker coverage for the placeholder endpoint host.
- Required parsed WatchKit alarm endpoint URLs to use the explicit `/alarm`
  path before sending alarm requests.
- Added static checker coverage for endpoint path validation.
- Required the parsed WatchKit alarm endpoint scheme to be exactly HTTPS before
  sending alarm requests.
- Added static checker coverage for parsed endpoint scheme validation.
- Rejected WatchKit alarm endpoint URLs that include query strings or fragments.
- Rejected WatchKit alarm endpoint URLs that embed usernames or passwords
  before the extension can send an alarm request.
- Replaced implicitly unwrapped WatchKit outlets in the alarm interface
  controller with optional outlets and nil-safe label updates, with static
  contracts to keep disconnected storyboard outlets from crashing the sample.
- Required `AlarmEndpointURL` to parse as an HTTPS URL with a host before the
  WatchKit extension sends the alarm request.

## 2026-06-08

- Added static contracts for the WatchKit alarm endpoint, HTTPS transport expectation, and workspace wiring.
- Added `make check` as the local verification entry point when Xcode is unavailable.
- Expanded the static contracts to cover WatchKit plist links, notification
  payload JSON, Xcode target types, and legacy CocoaPods pins.
- Added source-level alarm-hour normalization so the WatchKit request path
  mirrors the storyboard's 5 through 11 slider range.
