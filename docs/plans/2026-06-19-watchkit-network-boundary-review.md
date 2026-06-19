# WatchKit Network Boundary Review

Status: Completed

## Scope

Review the complete alarm submission path on the aggregate `#3` through `#16`
stack: plist configuration, URL parsing, destination policy, POST encoding,
ephemeral session state, redirects, timeouts, response metadata and body
handling, cancellation, completion ownership, UI lifecycle, and CI evidence.

## Findings

1. The Swift URL checks accepted localhost, private/link-local IP literals,
   legacy numeric IPv4 forms, local DNS suffixes, and IDN input. A locally
   configured endpoint such as `https://169.254.169.254/alarm` therefore passed
   validation and could transmit the selected alarm value to a private service.
2. Alamofire 1.2.1's data-task delegate appends every received chunk to an
   `NSMutableData` before `Request.response` runs. The WatchKit controller did
   not consume the response body, but a server could still force the extension
   to buffer an unbounded response until the resource timeout.
3. `make check` attempted an unsupported WatchKit 1 / Swift 1 build whenever a
   modern Xcode happened to be installed, making the portable baseline fail for
   toolchain reasons unrelated to the reviewed contracts.

## Root Cause And Provenance

- The endpoint validator introduced by `1b9bf94` and expanded by the later URL
  guard commits validated syntax but never established a public-DNS-only
  destination invariant. Confidence: clear from bounded history and executable
  Foundation URL probes.
- The original `988c104` Alamofire request already used the dependency's
  buffering data-task path. `c7098b2` made response completion explicit while
  carrying that buffering behavior forward. Confidence: clear from repository
  history and the pinned Alamofire 1.2.1 source.

## Design

- Add one Objective-C `AlarmNetworkPolicy` compiled into the WatchKit extension
  and imported through its bridging header. This keeps URL and response rules in
  a Foundation-native seam that both the historical Swift target and current
  native tests can exercise.
- Accept only canonical ASCII HTTPS DNS names with at least two valid labels,
  no IDN/punycode labels, no explicit port/userinfo/query/fragment, and the exact
  percent-encoded `/alarm` path. Reject reserved, localhost, `.local`,
  `.internal`, `.home.arpa`, IP-literal, and legacy numeric-host forms.
- Validate final response URL, 2xx status, declared content length, and declared
  JSON/plain-text media types. Intercept Alamofire's manager-level data callback
  so response bytes are discarded rather than appended and cancel after 4096
  bytes.
- Preserve the dedicated ephemeral manager, disabled cookie/cache/credential
  stores, redirect refusal, 10/15-second timeouts, POST body, current-request
  identity check, main-queue Alamofire completion, and deactivation cancellation.

## DNS Limitation

The policy validates URL text and rejects direct local/private destination
forms. It does not pin DNS answers or prevent a trusted public hostname from
resolving or rebinding to a private address after validation. Configure only an
authorized, static endpoint and apply DNS/egress controls at the service and
network boundary when this sample is adapted for production.

## Verification

- Native Objective-C policy and body-gate tests with Foundation.
- iOS 8 deployment-target Objective-C syntax and API availability checks.
- `NSURLProtocol` fake-network success and oversized-body cancellation tests.
- Structural source/project/workflow contracts.
- Seven hostile mutations covering response interception, target membership,
  bridging, private-host rejection, media type validation, body cap, and the
  inclusive byte boundary.
- Python 3.10, 3.12, and 3.14 portable gates.
- External-directory Make execution and `git diff --check`.
- Hosted Linux static and macOS native jobs.

No live alarm endpoint, historical Xcode 6 build, Watch simulator, paired watch,
or physical device was used. Those rows remain explicitly unexecuted in
`DEVICE_VERIFICATION.md`.
