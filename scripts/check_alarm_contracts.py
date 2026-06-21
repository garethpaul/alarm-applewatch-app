#!/usr/bin/env python3
"""Static contracts for the legacy Alarm WatchKit sample."""

import json
from pathlib import Path
import plistlib
import re
import sys
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "AGENTS.md",
    "Alarm.xcworkspace/contents.xcworkspacedata",
    "Alarm.xcodeproj/project.pbxproj",
    "Alarm/Info.plist",
    "Alarm WatchKit App/Info.plist",
    "Alarm WatchKit Extension/Info.plist",
    "Alarm WatchKit Extension/AlarmNetworkPolicy.h",
    "Alarm WatchKit Extension/AlarmNetworkPolicy.m",
    "Alarm WatchKit Extension/Alarm WatchKit Extension-Bridging-Header.h",
    "Alarm WatchKit Extension/InterfaceController.swift",
    "Alarm WatchKit Extension/NotificationController.swift",
    "Alarm WatchKit Extension/PushNotificationPayload.apns",
    "Alarm WatchKit App/Base.lproj/Interface.storyboard",
    "AlarmTests/AlarmTests.swift",
    "AlarmTests/Info.plist",
    "docs/plans/2026-06-12-watchkit-nonfinite-alarm-hour.md",
    "docs/plans/2026-06-13-watchkit-placeholder-host-canonicalization.md",
    "docs/plans/2026-06-13-watchkit-post-alarm-submission.md",
    "docs/plans/2026-06-13-watchkit-endpoint-scheme-canonicalization.md",
    "docs/plans/2026-06-14-watchkit-alarm-redirect-rejection.md",
    "docs/plans/2026-06-14-watchkit-device-verification-checklist.md",
    "docs/plans/2026-06-14-watchkit-endpoint-port-guard.md",
    "docs/plans/2026-06-15-watchkit-isolated-redirect-manager.md",
    "docs/plans/2026-06-15-watchkit-alarm-request-timeouts.md",
    "docs/plans/2026-06-19-watchkit-network-boundary-review.md",
    "DEVICE_VERIFICATION.md",
    "docs/device-preview.svg",
    "docs/readme-overview.svg",
    "Podfile",
    "Podfile.lock",
    "README.md",
    "SECURITY.md",
    ".github/workflows/check.yml",
]

WATCH_APP_BUNDLE_ID = "com.requestlabs.Alarm.watchkitapp"
WATCH_EXTENSION_BUNDLE_ID = "com.requestlabs.Alarm.watchkitextension"


def read_text(relative_path, failures):
    path = ROOT / relative_path
    if not path.exists():
        failures.append(f"{relative_path} is missing")
        return ""
    return path.read_text(encoding="utf-8")


def read_plist(relative_path, failures):
    path = ROOT / relative_path
    if not path.exists():
        failures.append(f"{relative_path} is missing")
        return {}
    try:
        with path.open("rb") as plist_file:
            return plistlib.load(plist_file)
    except Exception as exc:
        failures.append(f"{relative_path} is not readable as a plist: {exc}")
        return {}


def check_svg(relative_path, failures):
    path = ROOT / relative_path
    if not path.exists():
        failures.append(f"{relative_path} is missing")
        return
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        failures.append(f"{relative_path} is not valid XML: {exc}")
        return
    require(root.tag.endswith("svg"), f"{relative_path} must have an SVG root element", failures)
    require("viewBox" in root.attrib, f"{relative_path} must define a viewBox", failures)


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def require_equal(actual, expected, message, failures):
    if actual != expected:
        failures.append(f"{message}: expected {expected!r}, got {actual!r}")


def require_contains(text, expected, message, failures):
    require(expected in text, f"{message}: missing {expected!r}", failures)


def require_regex(text, pattern, message, failures):
    require(
        re.search(pattern, text, re.MULTILINE | re.DOTALL) is not None,
        message,
        failures,
    )


def workflow_action_blocks(workflow, action):
    lines = workflow.splitlines()
    action_line = f"uses: {action}"
    blocks = []

    for index, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line == action_line or stripped_line.startswith(f"{action_line} #"):
            indentation = len(line) - len(line.lstrip())
            block = [line]
            for following_line in lines[index + 1 :]:
                following_indentation = len(following_line) - len(
                    following_line.lstrip()
                )
                if (
                    following_line.lstrip().startswith("- ")
                    and following_indentation <= indentation
                ):
                    break
                block.append(following_line)
            blocks.append("\n".join(block))

    return blocks


def require_no_arbitrary_loads(plist, label, failures):
    def walk(value):
        if isinstance(value, dict):
            if value.get("NSAllowsArbitraryLoads") is True:
                return True
            return any(walk(child) for child in value.values())
        if isinstance(value, list):
            return any(walk(child) for child in value)
        return False

    require(not walk(plist), f"{label} must not enable arbitrary ATS loads", failures)


def require_no_secret_like_plist_values(plist, label, failures):
    secret_key = re.compile(
        r"(api[_-]?key|client[_-]?secret|password|private[_-]?key|secret|token)",
        re.IGNORECASE,
    )

    def walk(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}"
                if secret_key.search(str(key)) and child not in ("", None):
                    if not (isinstance(child, str) and child.startswith("$(")):
                        failures.append(f"{label} has possible committed secret value at {child_path}")
                walk(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")

    walk(plist, label)


def check_required_files(failures):
    for relative_path in REQUIRED_FILES:
        require((ROOT / relative_path).exists(), f"{relative_path} is missing", failures)


def check_alarm_endpoint(interface, network_policy, extension_plist, failures):
    endpoint = extension_plist.get("AlarmEndpointURL")
    parsed_endpoint = urlparse(endpoint) if isinstance(endpoint, str) else None

    require(
        "http://myhome.com/alarm" not in interface,
        "alarm endpoint must not be hardcoded as a plain HTTP source value",
        failures,
    )
    require_contains(
        interface,
        'objectForInfoDictionaryKey("AlarmEndpointURL")',
        "InterfaceController must read AlarmEndpointURL from extension Info.plist",
        failures,
    )
    require(
        'hasPrefix("https://")' not in interface,
        "InterfaceController must not use a case-sensitive raw HTTPS prefix gate",
        failures,
    )
    require_contains(
        interface,
        "AlarmNetworkPolicy.validatedEndpointURL(endpoint)",
        "InterfaceController must delegate endpoint parsing to the native policy",
        failures,
    )
    require_regex(
        network_policy,
        r'percentEncodedPath\s+isEqualToString:@"/alarm"',
        "alarm endpoint path must stay explicit as a named constant",
        failures,
    )
    require_contains(
        network_policy,
        "+ (NSString *)canonicalHost:(NSString *)host",
        "native endpoint policy must canonicalize parsed hosts",
        failures,
    )
    require_contains(
        network_policy,
        "+ (BOOL)isDisallowedHost:(NSString *)host",
        "native endpoint policy must classify reserved and local hosts",
        failures,
    )
    require(
        '@"invalid"' in network_policy
        and '@"localhost"' in network_policy
        and '@"local"' in network_policy
        and '@"internal"' in network_policy
        and '@"home.arpa"' in network_policy,
        "native endpoint policy must reject reserved and local DNS suffixes",
        failures,
    )
    require_contains(
        network_policy,
        "NSASCIIStringEncoding",
        "native endpoint policy must reject non-ASCII and IDN input",
        failures,
    )
    require(
        '@"xn--"' in network_policy and 'componentsSeparatedByString:@"."' in network_policy,
        "native endpoint policy must reject IDN labels and validate DNS labels",
        failures,
    )
    require_contains(
        network_policy,
        "componentsWithString:trimmed",
        "native endpoint policy must parse AlarmEndpointURL before use",
        failures,
    )
    require_contains(
        network_policy,
        '[components.scheme caseInsensitiveCompare:@"https"]',
        "native endpoint policy must require HTTPS case-insensitively",
        failures,
    )
    require_contains(
        network_policy,
        "components.port != nil",
        "native endpoint policy must reject explicit ports",
        failures,
    )
    require(
        "components.port == @443" not in network_policy,
        "native endpoint policy must not allow explicit default ports",
        failures,
    )
    for boundary in ("components.user != nil", "components.password != nil", "components.query != nil", "components.fragment != nil"):
        require_contains(network_policy, boundary, f"native endpoint policy must enforce {boundary}", failures)
    require_contains(
        interface,
        "if let endpoint = alarmEndpointURL()",
        "setAlarm must skip network requests when the endpoint is not configured",
        failures,
    )
    require_contains(
        interface,
        "alarmRequestManager.request(.POST, endpoint, parameters: alarmParameters())",
        "alarm request must POST to the validated endpoint with normalized parameters",
        failures,
    )
    require(
        "Alamofire.request(.GET" not in interface
        and "alarmRequestManager.request(.GET" not in interface,
        "alarm submissions must not encode alarmTime into a GET request URL",
        failures,
    )
    require_regex(
        interface,
        r"private\s+let\s+alarmTimeParameter\s*=\s*\"alarmTime\"",
        "alarm time parameter must stay explicit as a named constant",
        failures,
    )
    require_regex(
        interface,
        r"func\s+alarmParameters\(\)\s*->\s*\[String:\s*String\]\s*\{\s*"
        r"return\s*\[\s*alarmTimeParameter\s*:\s*String\(normalizedAlarmHour\(wakeUp\)\)\s*\]",
        "alarm parameters must use alarmTimeParameter and the normalized wakeUp value",
        failures,
    )
    require(
        parsed_endpoint is not None
        and parsed_endpoint.scheme == "https"
        and bool(parsed_endpoint.netloc),
        "extension Info.plist must define an HTTPS AlarmEndpointURL placeholder with a host",
        failures,
    )
    require(
        isinstance(endpoint, str) and "myhome.com" not in endpoint,
        "extension Info.plist must not keep the old myhome.com endpoint",
        failures,
    )
    require(
        parsed_endpoint is not None and parsed_endpoint.hostname == "example.invalid",
        "extension Info.plist AlarmEndpointURL placeholder must stay on example.invalid",
        failures,
    )
    require(
        parsed_endpoint is not None
        and parsed_endpoint.username is None
        and parsed_endpoint.password is None,
        "extension Info.plist AlarmEndpointURL placeholder must not include credentials",
        failures,
    )
    require(
        parsed_endpoint is not None
        and parsed_endpoint.query == ""
        and parsed_endpoint.fragment == "",
        "extension Info.plist AlarmEndpointURL placeholder must not include query strings or fragments",
        failures,
    )
    require(
        parsed_endpoint is not None and parsed_endpoint.path == "/alarm",
        "extension Info.plist AlarmEndpointURL placeholder must use the /alarm path",
        failures,
    )


def check_alarm_hour_bounds(interface, storyboard, failures):
    require_contains(
        interface,
        "private let minimumAlarmHour = 5",
        "InterfaceController must keep the minimum alarm hour explicit",
        failures,
    )
    require_contains(
        interface,
        "private let maximumAlarmHour = 11",
        "InterfaceController must keep the maximum alarm hour explicit",
        failures,
    )
    require_regex(
        interface,
        r"func\s+normalizedAlarmHour\(hour:\s*Int\)\s*->\s*Int\s*\{.*"
        r"hour\s*<\s*minimumAlarmHour.*hour\s*>\s*maximumAlarmHour",
        "InterfaceController must clamp alarm hours to the documented range",
        failures,
    )
    float_normalizer_start = interface.find("func normalizedAlarmHour(value: Float)")
    float_normalizer_end = interface.find(
        "func alarmDisplayText", float_normalizer_start
    )
    float_normalizer = (
        interface[float_normalizer_start:float_normalizer_end]
        if float_normalizer_start >= 0 and float_normalizer_end >= 0
        else ""
    )
    require(
        "if value != value" in float_normalizer
        and "if value < Float(minimumAlarmHour)" in float_normalizer
        and "if value > Float(maximumAlarmHour)" in float_normalizer
        and "normalizedAlarmHour(Int(value))" in float_normalizer
        and float_normalizer.index("if value != value")
        < float_normalizer.index("normalizedAlarmHour(Int(value))")
        and float_normalizer.index("if value < Float(minimumAlarmHour)")
        < float_normalizer.index("normalizedAlarmHour(Int(value))")
        and float_normalizer.index("if value > Float(maximumAlarmHour)")
        < float_normalizer.index("normalizedAlarmHour(Int(value))"),
        "Float alarm values must reject NaN and clamp extremes before Int conversion",
        failures,
    )
    require_contains(
        interface,
        "wakeUp = normalizedAlarmHour(value)",
        "slider updates must normalize the selected alarm hour",
        failures,
    )
    require_contains(
        interface,
        "alarmValue?.setText(alarmDisplayText(wakeUp))",
        "alarm display text must use the normalized display helper with nil-safe outlet updates",
        failures,
    )
    require_contains(
        interface,
        "String(normalizedAlarmHour(wakeUp))",
        "alarm request parameters must use a normalized alarm hour",
        failures,
    )
    require_contains(
        storyboard,
        '<slider width="1" alignment="center" value="5" minimum="5" maximum="11" steps="6"',
        "WatchKit storyboard slider must preserve the 5 through 11 hour range",
        failures,
    )


def check_watchkit_outlet_safety(interface, failures):
    require_contains(
        interface,
        "@IBOutlet weak var slider: WKInterfaceSlider?",
        "slider outlet must not be an implicitly unwrapped optional",
        failures,
    )
    require_contains(
        interface,
        "@IBOutlet weak var alarmValue: WKInterfaceLabel?",
        "alarmValue outlet must not be an implicitly unwrapped optional",
        failures,
    )
    require(
        "WKInterfaceSlider!" not in interface and "WKInterfaceLabel!" not in interface,
        "WatchKit outlets must avoid implicitly unwrapped optionals",
        failures,
    )
    require(
        interface.count("alarmValue?.setText(alarmDisplayText(wakeUp))") >= 2,
        "all alarm label updates must use optional chaining",
        failures,
    )


def check_alarm_request_lifecycle(interface, failures):
    require_contains(
        interface,
        "private var alarmRequest: Request?",
        "InterfaceController must retain at most one alarm request",
        failures,
    )
    require_regex(
        interface,
        r"@IBAction\s+func\s+setAlarm\(\)\s*\{\s*"
        r"alarmRequest\?\.cancel\(\)\s*alarmRequest\s*=\s*nil.*"
        r"let\s+request\s*=\s*alarmRequestManager\.request\(\.POST,\s*endpoint,\s*"
        r"parameters:\s*alarmParameters\(\)\)\s*alarmRequest\s*=\s*request",
        "setAlarm must cancel any prior request before retaining its replacement",
        failures,
    )
    require_regex(
        interface,
        r"override\s+func\s+didDeactivate\(\)\s*\{.*"
        r"alarmRequest\?\.cancel\(\)\s*alarmRequest\s*=\s*nil\s*"
        r"super\.didDeactivate\(\)",
        "didDeactivate must cancel and release the outstanding alarm request",
        failures,
    )
    require(
        interface.count("alarmRequestManager.request(") == 1
        and "Alamofire.request(" not in interface,
        "InterfaceController must keep a single alarm request creation path",
        failures,
    )
    require_regex(
        interface,
        r"let\s+request\s*=\s*alarmRequestManager\.request\(\.POST,\s*endpoint,\s*"
        r"parameters:\s*alarmParameters\(\)\)\s*alarmRequest\s*=\s*request\s*"
        r"request\.validate\(\)\.response\s*\{\s*\[weak\s+self\]",
        "setAlarm must retain and validate one request before observing completion",
        failures,
    )
    require_regex(
        interface,
        r"if\s+let\s+controller\s*=\s*self\s*\{\s*"
        r"if\s+controller\.alarmRequest\s*===\s*request\s*\{\s*"
        r"controller\.alarmRequest\s*=\s*nil\s*"
        r"if\s+error\s*!=\s*nil\s*\{\s*"
        r'NSLog\("Alarm submission failed\."\)',
        "alarm completion must clear and report only the still-current failed request",
        failures,
    )
    require(
        interface.count('NSLog("Alarm submission failed.")') == 1
        and "NSLog(error" not in interface
        and "NSLog(\"%@\"" not in interface,
        "alarm completion must keep one generic failure log without dependency details",
        failures,
    )


def check_plist_contracts(app, watch_app, extension, tests, failures):
    require_equal(app.get("CFBundlePackageType"), "APPL", "iOS app package type", failures)
    require_equal(
        app.get("CFBundleIdentifier"),
        "com.requestlabs.$(PRODUCT_NAME:rfc1034identifier)",
        "iOS app bundle id template",
        failures,
    )
    require_equal(app.get("UIMainStoryboardFile"), "Main", "iOS app main storyboard", failures)
    require_equal(app.get("UILaunchStoryboardName"), "LaunchScreen", "iOS app launch storyboard", failures)

    require_equal(watch_app.get("CFBundleIdentifier"), WATCH_APP_BUNDLE_ID, "WatchKit app bundle id", failures)
    require_equal(watch_app.get("CFBundlePackageType"), "APPL", "WatchKit app package type", failures)
    require_equal(watch_app.get("WKWatchKitApp"), True, "WatchKit app flag", failures)
    require_equal(
        watch_app.get("WKCompanionAppBundleIdentifier"),
        "com.requestlabs.Alarm",
        "WatchKit companion app bundle id",
        failures,
    )

    require_equal(
        extension.get("CFBundleIdentifier"),
        WATCH_EXTENSION_BUNDLE_ID,
        "WatchKit extension bundle id",
        failures,
    )
    require_equal(extension.get("CFBundlePackageType"), "XPC!", "WatchKit extension package type", failures)
    require_equal(
        extension.get("RemoteInterfacePrincipalClass"),
        "$(PRODUCT_MODULE_NAME).InterfaceController",
        "WatchKit extension principal class",
        failures,
    )

    ns_extension = extension.get("NSExtension", {})
    require_equal(
        ns_extension.get("NSExtensionPointIdentifier"),
        "com.apple.watchkit",
        "WatchKit extension point",
        failures,
    )
    require_equal(
        ns_extension.get("NSExtensionAttributes", {}).get("WKAppBundleIdentifier"),
        WATCH_APP_BUNDLE_ID,
        "WatchKit extension links to WatchKit app bundle id",
        failures,
    )

    require_equal(tests.get("CFBundlePackageType"), "BNDL", "unit test bundle package type", failures)

    for label, plist in [
        ("Alarm/Info.plist", app),
        ("Alarm WatchKit App/Info.plist", watch_app),
        ("Alarm WatchKit Extension/Info.plist", extension),
        ("AlarmTests/Info.plist", tests),
    ]:
        require_no_arbitrary_loads(plist, label, failures)
        require_no_secret_like_plist_values(plist, label, failures)


def check_push_payload(failures):
    payload_text = read_text("Alarm WatchKit Extension/PushNotificationPayload.apns", failures)
    try:
        payload = json.loads(payload_text)
    except ValueError as exc:
        failures.append(f"push notification payload is invalid JSON: {exc}")
        return

    aps = payload.get("aps", {})
    alert = aps.get("alert", {})
    require_equal(aps.get("category"), "myCategory", "push payload category", failures)
    require_equal(alert.get("body"), "Test message", "push payload alert body", failures)
    require_equal(alert.get("title"), "Optional title", "push payload alert title", failures)

    actions = payload.get("WatchKit Simulator Actions")
    require(isinstance(actions, list) and len(actions) > 0, "push payload must include simulator actions", failures)
    if isinstance(actions, list) and actions:
        require_equal(actions[0].get("identifier"), "firstButtonAction", "push payload first action id", failures)


def check_dependency_and_project_contracts(project, podfile, podfile_lock, failures):
    require_contains(podfile, "platform :ios, '8.0'", "Podfile must preserve legacy iOS platform", failures)
    require_contains(podfile, "target 'Alarm WatchKit Extension' do", "Podfile must include extension target", failures)
    require_contains(podfile, "target 'Alarm WatchKit App' do", "Podfile must include WatchKit app target", failures)
    require(
        podfile.count("pod 'Alamofire', '~> 1.2'") == 2,
        "Podfile must declare Alamofire ~> 1.2 for both WatchKit targets",
        failures,
    )
    require_contains(podfile_lock, "- Alamofire (1.2.1)", "Podfile.lock must pin Alamofire 1.2.1", failures)
    require_contains(podfile_lock, "COCOAPODS: 0.37.0.beta.1", "Podfile.lock must pin CocoaPods era", failures)

    require_contains(
        project,
        'productType = "com.apple.product-type.application";',
        "project must keep iOS app target",
        failures,
    )
    require_contains(
        project,
        'productType = "com.apple.product-type.bundle.unit-test";',
        "project must keep test target",
        failures,
    )
    require_contains(
        project,
        'productType = "com.apple.product-type.watchkit-extension";',
        "project must keep WatchKit extension target",
        failures,
    )
    require_contains(
        project,
        'productType = "com.apple.product-type.application.watchapp";',
        "project must keep WatchKit app target",
        failures,
    )
    require_contains(
        project,
        'INFOPLIST_FILE = "Alarm WatchKit Extension/Info.plist";',
        "Xcode project must keep the WatchKit extension plist wired",
        failures,
    )


def check_ci(makefile, workflow, failures):
    checkout_action = "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10"
    require_contains(
        makefile,
        "override ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))",
        "Makefile must protect repository paths from command-line overrides",
        failures,
    )
    require_contains(
        makefile,
        "PYTHON ?= python3",
        "Makefile must preserve the Python command override",
        failures,
    )
    require_contains(
        makefile,
        "$(ROOT)scripts/check_alarm_contracts.py",
        "Makefile must use the rooted contract checker path",
        failures,
    )
    require_contains(
        makefile,
        "cd $(ROOT) && xcodebuild -workspace Alarm.xcworkspace",
        "Makefile must run Xcode from the repository root",
        failures,
    )
    require_regex(
        makefile,
        r"^ci:\s+lint\s+test\s+mutation-test$",
        "Makefile must expose deterministic lint, test, and mutation CI checks",
        failures,
    )
    ci_target = re.search(r"^ci:[^\n]*(?:\n\t[^\n]*)*", makefile, re.MULTILINE)
    require(
        ci_target is not None and "xcodebuild" not in ci_target.group(0),
        "Makefile CI target must not invoke xcodebuild",
        failures,
    )
    require_regex(
        workflow,
        r"^permissions:\s*\n  contents: read\s*\n\s*^concurrency:",
        "CI workflow must use read-only repository permissions",
        failures,
    )
    require_contains(workflow, "pull_request:", "CI workflow must run for pull requests", failures)
    require_contains(workflow, "push:", "CI workflow must run for pushes", failures)
    require_contains(
        workflow,
        "timeout-minutes: 5",
        "CI workflow must have a bounded timeout",
        failures,
    )
    require_contains(
        workflow,
        "runs-on: ubuntu-24.04",
        "CI workflow must use a fixed Ubuntu runner image",
        failures,
    )
    require_contains(
        workflow,
        "cancel-in-progress: true",
        "CI workflow must cancel superseded runs",
        failures,
    )
    require_contains(
        workflow,
        checkout_action,
        "CI workflow must pin actions/checkout",
        failures,
    )
    require_contains(
        workflow,
        "persist-credentials: false",
        "CI workflow must not persist checkout credentials",
        failures,
    )
    require_equal(
        workflow.count("persist-credentials:"),
        2,
        "each CI checkout must disable credential persistence exactly once",
        failures,
    )
    require(
        "persist-credentials: true" not in workflow,
        "CI workflow must never enable checkout credential persistence",
        failures,
    )
    checkout_steps = workflow_action_blocks(workflow, checkout_action)
    require_equal(
        len(checkout_steps),
        2,
        "CI workflow must contain both reviewed checkout steps",
        failures,
    )
    for index, checkout_step in enumerate(checkout_steps, start=1):
        require_contains(
            checkout_step,
            "\n        with:\n          persist-credentials: false",
            f"checkout step {index} must disable credential persistence "
            "in its with block",
            failures,
        )
    require_contains(
        workflow,
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        "CI workflow must pin actions/setup-python",
        failures,
    )
    require_contains(
        workflow,
        'python-version: ["3.10", "3.12", "3.14"]',
        "CI workflow must cover Python 3.10, 3.12, and 3.14",
        failures,
    )
    require_contains(
        workflow,
        "workflow_dispatch:",
        "CI workflow must support manual dispatch",
        failures,
    )
    require(
        "pull_request_target:" not in workflow,
        "CI workflow must not use pull_request_target",
        failures,
    )
    action_uses = re.findall(r"^\s*-?\s*uses:\s*([^\s#]+)", workflow, re.MULTILINE)
    require_equal(
        action_uses,
        [
            checkout_action,
            "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
            checkout_action,
        ],
        "CI workflow must use only the reviewed pinned actions",
        failures,
    )
    require_contains(workflow, "run: make ci", "CI workflow must run the shared CI target", failures)


def check_docs(readme, security, changes, endpoint_plan, placeholder_plan, inert_placeholder_plan, ci_plan, failures):
    require_contains(readme, "docs/readme-overview.svg", "README must embed the project overview", failures)
    require_contains(readme, "docs/device-preview.svg", "README must embed the device preview", failures)
    require_contains(readme, "Alarm.xcworkspace", "README must direct maintainers to open the workspace", failures)
    require_contains(readme, "make check", "README must document local verification", failures)
    require_contains(readme, "make ci", "README must document deterministic CI verification", failures)
    require_contains(readme, "AlarmEndpointURL", "README must document endpoint configuration", failures)
    require_contains(changes, "static contracts", "CHANGES must mention static contract coverage", failures)
    require_contains(endpoint_plan, "AlarmEndpointURL", "endpoint plan must document the plist-backed endpoint", failures)
    require_contains(placeholder_plan, "Status: Completed", "placeholder endpoint plan must be completed", failures)
    require_contains(placeholder_plan, "make check", "placeholder endpoint plan must record make check", failures)
    require_contains(inert_placeholder_plan, "Status: Completed", "inert placeholder plan must be completed", failures)
    require_contains(inert_placeholder_plan, "make check", "inert placeholder plan must record make check", failures)
    require_contains(readme, "example.invalid", "README must document the inert endpoint placeholder", failures)
    for label, text in {
        "README": readme,
        "SECURITY": security,
        "CHANGES": changes,
    }.items():
        require_contains(
            text,
            "case-insensitive",
            f"{label} must document case-insensitive placeholder-host rejection",
            failures,
        )
        require_contains(
            text,
            "trailing root dot",
            f"{label} must document trailing-root-dot placeholder rejection",
            failures,
        )
        require_contains(
            text,
            "POST",
            f"{label} must document POST alarm submission",
            failures,
        )
        require_regex(
            text,
            r"request\s+URLs?",
            f"{label} must document alarmTime URL minimization",
            failures,
        )
    require_contains(ci_plan, "Status: Completed", "CI baseline plan must be completed", failures)


def main():
    failures = []

    check_required_files(failures)
    check_svg("docs/readme-overview.svg", failures)
    check_svg("docs/device-preview.svg", failures)

    interface = read_text("Alarm WatchKit Extension/InterfaceController.swift", failures)
    network_policy = read_text("Alarm WatchKit Extension/AlarmNetworkPolicy.m", failures)
    storyboard = read_text("Alarm WatchKit App/Base.lproj/Interface.storyboard", failures)
    project = read_text("Alarm.xcodeproj/project.pbxproj", failures)
    podfile = read_text("Podfile", failures)
    podfile_lock = read_text("Podfile.lock", failures)
    makefile = read_text("Makefile", failures)
    workflow = read_text(".github/workflows/check.yml", failures)
    readme = read_text("README.md", failures)
    security = read_text("SECURITY.md", failures)
    vision = read_text("VISION.md", failures)
    changes = read_text("CHANGES.md", failures)
    agents = read_text("AGENTS.md", failures)
    endpoint_plan = read_text("docs/plans/2026-06-08-watchkit-endpoint-contracts.md", failures)
    placeholder_plan = read_text("docs/plans/2026-06-09-watchkit-endpoint-placeholder-host.md", failures)
    inert_placeholder_plan = read_text("docs/plans/2026-06-10-watchkit-inert-endpoint-placeholder.md", failures)
    ci_plan = read_text("docs/plans/2026-06-10-watchkit-ci-baseline.md", failures)
    nonfinite_alarm_plan = read_text(
        "docs/plans/2026-06-12-watchkit-nonfinite-alarm-hour.md", failures
    )
    canonical_host_plan = read_text(
        "docs/plans/2026-06-13-watchkit-placeholder-host-canonicalization.md",
        failures,
    )
    post_submission_plan = read_text(
        "docs/plans/2026-06-13-watchkit-post-alarm-submission.md", failures
    )
    placeholder_suffix_plan = read_text(
        "docs/plans/2026-06-13-watchkit-placeholder-domain-suffix.md", failures
    )
    scheme_canonicalization_plan = read_text(
        "docs/plans/2026-06-13-watchkit-endpoint-scheme-canonicalization.md",
        failures,
    )
    make_root_plan = read_text(
        "docs/plans/2026-06-14-make-root-override-protection.md", failures
    )
    response_completion_plan = read_text(
        "docs/plans/2026-06-14-watchkit-alarm-response-completion.md", failures
    )
    redirect_plan = read_text(
        "docs/plans/2026-06-14-watchkit-alarm-redirect-rejection.md", failures
    )
    device_verification_plan = read_text(
        "docs/plans/2026-06-14-watchkit-device-verification-checklist.md",
        failures,
    )
    endpoint_port_plan = read_text(
        "docs/plans/2026-06-14-watchkit-endpoint-port-guard.md", failures
    )
    isolated_redirect_plan = read_text(
        "docs/plans/2026-06-15-watchkit-isolated-redirect-manager.md", failures
    )
    request_timeout_plan = read_text(
        "docs/plans/2026-06-15-watchkit-alarm-request-timeouts.md", failures
    )
    ephemeral_session_plan = read_text(
        "docs/plans/2026-06-15-watchkit-ephemeral-alarm-session.md", failures
    )
    session_storage_plan = read_text(
        "docs/plans/2026-06-17-watchkit-session-storage-isolation.md", failures
    )
    device_verification = read_text("DEVICE_VERIFICATION.md", failures)

    app = read_plist("Alarm/Info.plist", failures)
    watch_app = read_plist("Alarm WatchKit App/Info.plist", failures)
    extension = read_plist("Alarm WatchKit Extension/Info.plist", failures)
    tests = read_plist("AlarmTests/Info.plist", failures)

    check_alarm_endpoint(interface, network_policy, extension, failures)
    check_alarm_hour_bounds(interface, storyboard, failures)
    check_watchkit_outlet_safety(interface, failures)
    check_alarm_request_lifecycle(interface, failures)
    require_regex(
        interface,
        r"private\s+let\s+alarmRequestManager:\s*Manager\s*=\s*\{\s*"
        r"let\s+configuration\s*=\s*NSURLSessionConfiguration\.ephemeralSessionConfiguration\(\)\s*"
        r"configuration\.HTTPShouldSetCookies\s*=\s*false\s*"
        r"configuration\.HTTPCookieStorage\s*=\s*nil\s*"
        r"configuration\.URLCredentialStorage\s*=\s*nil\s*"
        r"configuration\.URLCache\s*=\s*nil\s*"
        r"configuration\.HTTPAdditionalHeaders\s*=\s*Manager\.defaultHTTPHeaders\s*"
        r"configuration\.timeoutIntervalForRequest\s*=\s*alarmRequestTimeout\s*"
        r"configuration\.timeoutIntervalForResource\s*=\s*alarmResourceTimeout\s*"
        r"let\s+manager\s*=\s*Manager\(configuration:\s*configuration\)",
        "alarm submissions must use a dedicated bounded ephemeral Alamofire manager",
        failures,
    )
    for label, text in (
        ("README", readme),
        ("security guidance", security),
        ("vision", vision),
        ("agent guidance", agents),
        ("changes", changes),
    ):
        require_contains(
            text,
            "Alarm submissions disable cookie, credential, and cache stores so one request cannot influence the next.",
            f"{label} must document alarm session storage isolation",
            failures,
        )
    for contract in (
        "Status: Completed",
        "HTTPShouldSetCookies",
        "HTTPCookieStorage",
        "URLCredentialStorage",
        "URLCache",
        "make check",
        "hostile mutations",
    ):
        require_contains(
            session_storage_plan,
            contract,
            f"session storage isolation plan must keep contract: {contract}",
            failures,
        )
    for label, text in (
        ("README", readme),
        ("security guidance", security),
        ("vision", vision),
        ("agent guidance", agents),
        ("changes", changes),
    ):
        require_contains(
            text,
            "Alarm submissions use an ephemeral session so cookies, credentials, and cache data are not persisted.",
            f"{label} must document ephemeral alarm session privacy",
            failures,
        )
    for contract in (
        "Status: Completed",
        "ephemeralSessionConfiguration",
        "make check",
        "hostile mutations",
    ):
        require_contains(
            ephemeral_session_plan,
            contract,
            f"ephemeral alarm session plan must keep contract: {contract}",
            failures,
        )
    require(
        "Manager.sharedInstance" not in interface,
        "alarm submissions must not mutate the process-wide Alamofire shared manager",
        failures,
    )
    require_regex(
        interface,
        r"taskWillPerformHTTPRedirection\s*=\s*\{\s*"
        r"\(_,\s*_,\s*_,\s*_\)\s+in\s*return\s+nil\s*\}",
        "alarm redirect hook must reject the follow-up request",
        failures,
    )
    require(
        0
        <= interface.find("taskWillPerformHTTPRedirection")
        < interface.find("return manager")
        < interface.find("alarmRequestManager.request(.POST"),
        "alarm redirect rejection must be configured before request creation",
        failures,
    )
    check_plist_contracts(app, watch_app, extension, tests, failures)
    check_push_payload(failures)
    check_dependency_and_project_contracts(project, podfile, podfile_lock, failures)
    check_ci(makefile, workflow, failures)
    check_docs(readme, security, changes, endpoint_plan, placeholder_plan, inert_placeholder_plan, ci_plan, failures)
    require_contains(
        nonfinite_alarm_plan,
        "Status: Completed",
        "non-finite alarm-hour plan must be completed",
        failures,
    )
    require_contains(
        nonfinite_alarm_plan,
        "make check",
        "non-finite alarm-hour plan must record make check",
        failures,
    )
    require_contains(
        canonical_host_plan,
        "Status: Completed",
        "placeholder-host canonicalization plan must be completed",
        failures,
    )
    require_contains(
        post_submission_plan,
        "Status: Completed",
        "POST alarm-submission plan must be completed",
        failures,
    )
    require_contains(
        placeholder_suffix_plan,
        "Status: Completed",
        "placeholder-domain suffix plan must be completed",
        failures,
    )
    require_contains(
        placeholder_suffix_plan,
        "hostile mutations",
        "placeholder-domain suffix plan must record hostile mutation evidence",
        failures,
    )
    require_contains(
        scheme_canonicalization_plan,
        "Status: Completed",
        "endpoint scheme canonicalization plan must be completed",
        failures,
    )
    require_contains(
        scheme_canonicalization_plan,
        "make check",
        "endpoint scheme canonicalization plan must record make check",
        failures,
    )
    require(
        "hostile mutations" in scheme_canonicalization_plan.lower(),
        "endpoint scheme canonicalization plan must record hostile mutations",
        failures,
    )
    require_contains(
        make_root_plan,
        "Status: Completed",
        "Make root protection plan must be completed",
        failures,
    )
    require_contains(
        make_root_plan,
        "make check",
        "Make root protection plan must record make check",
        failures,
    )
    require(
        "mutations" in make_root_plan.lower(),
        "Make root protection plan must record mutation evidence",
        failures,
    )
    require_contains(
        readme,
        "schemes are canonicalized case-insensitively",
        "README must document parsed endpoint scheme canonicalization",
        failures,
    )
    require_contains(
        security,
        "scheme is compared case-insensitively",
        "security guidance must document parsed endpoint scheme canonicalization",
        failures,
    )
    require_contains(
        vision,
        "Canonicalize parsed endpoint schemes case-insensitively",
        "vision must preserve parsed endpoint scheme canonicalization",
        failures,
    )
    require_contains(
        changes,
        "parsed HTTPS scheme validation case-insensitive",
        "changes must record parsed endpoint scheme canonicalization",
        failures,
    )
    require_contains(
        readme,
        "subdomains beneath `example.invalid`",
        "README must document reserved placeholder subdomain rejection",
        failures,
    )
    require_contains(
        security,
        "reserved placeholder domain",
        "security guidance must document the reserved placeholder domain boundary",
        failures,
    )
    require_contains(
        vision,
        "reserved placeholder subdomains",
        "vision must preserve reserved placeholder subdomain rejection",
        failures,
    )
    require_contains(
        changes,
        "placeholder subdomains",
        "changes must record placeholder subdomain rejection",
        failures,
    )
    require_contains(
        response_completion_plan,
        "Status: Completed",
        "alarm response completion plan must be completed",
        failures,
    )
    require_contains(
        response_completion_plan,
        "make check",
        "alarm response completion plan must record make check",
        failures,
    )
    require(
        "mutations" in response_completion_plan.lower(),
        "alarm response completion plan must record mutation evidence",
        failures,
    )
    require_contains(
        redirect_plan,
        "Status: Completed",
        "alarm redirect rejection plan must be completed",
        failures,
    )
    require_contains(
        redirect_plan,
        "make check",
        "alarm redirect rejection plan must record make check",
        failures,
    )
    require(
        "mutations" in redirect_plan.lower(),
        "alarm redirect rejection plan must record mutation evidence",
        failures,
    )
    require(
        re.search(r"rejects\s+redirect follow-up requests", readme)
        and re.search(r"reject\s+redirect follow-up requests", security)
        and "Reject alarm redirect follow-up requests" in vision
        and "Rejected alarm redirect follow-up requests" in changes,
        "alarm redirect rejection must remain documented",
        failures,
    )
    require_contains(
        readme,
        "Completed alarm requests clear only while still current",
        "README must document current-request completion handling",
        failures,
    )
    require_contains(
        security,
        "generic alarm submission failure",
        "security guidance must document generic alarm failure logging",
        failures,
    )
    require_contains(
        vision,
        "Validate alarm responses and ignore stale completion callbacks",
        "vision must preserve alarm response completion handling",
        failures,
    )
    require_contains(
        changes,
        "Validated alarm responses",
        "changes must record alarm response completion handling",
        failures,
    )
    require_contains(
        post_submission_plan,
        "make check",
        "POST alarm-submission plan must record make check",
        failures,
    )
    require_contains(
        post_submission_plan,
        "hostile mutations",
        "POST alarm-submission plan must record hostile mutations",
        failures,
    )
    require_contains(
        canonical_host_plan,
        "make check",
        "placeholder-host canonicalization plan must record make check",
        failures,
    )
    require_contains(
        canonical_host_plan,
        "hostile mutations",
        "placeholder-host canonicalization plan must record hostile mutations",
        failures,
    )
    for contract in (
        "commit SHA and pull request",
        "Open `Alarm.xcworkspace`",
        "Watch app deactivation",
        "Repeated submission",
        "Redirect response",
        "PushNotificationPayload.apns",
        "Do not convert `not run` into passing evidence.",
        "endpoint URL, alarm time, credentials",
        "every simulator and physical-device row as",
        "unexecuted",
    ):
        require_contains(
            device_verification,
            contract,
            "WatchKit device verification checklist must keep runtime evidence contract",
            failures,
        )
    require(
        "DEVICE_VERIFICATION.md" in readme
        and "keeping unexecuted rows explicit" in readme
        and "device verification matrix" in vision.lower()
        and "every runtime row explicitly unexecuted" in changes,
        "Repository guidance must document the unexecuted WatchKit runtime matrix",
        failures,
    )
    require(
        "Status: Completed" in device_verification_plan
        and "make check" in device_verification_plan
        and "hostile mutations" in device_verification_plan
        and "No Xcode, simulator, or physical-device scenario was executed"
        in device_verification_plan,
        "WatchKit device verification plan must record completed portable evidence and runtime non-claims",
        failures,
    )
    require(
        "Status: Completed" in endpoint_port_plan
        and "make check" in endpoint_port_plan
        and "hostile mutations" in endpoint_port_plan
        and "hosted" in endpoint_port_plan.lower(),
        "WatchKit endpoint port plan must record completed local and hosted verification boundaries",
        failures,
    )
    require(
        "default HTTPS port" in readme
        and "use no explicit port" in security
        and "explicit port" in changes,
        "Repository guidance must document the default-port-only alarm endpoint boundary",
        failures,
    )
    require(
        "dedicated Alamofire manager" in readme
        and "process-wide shared manager" in security
        and "dedicated Alamofire manager" in changes,
        "Repository guidance must document alarm redirect-manager isolation",
        failures,
    )
    require(
        "Status: Completed" in isolated_redirect_plan
        and "focused portable contract check" in isolated_redirect_plan
        and "repository-root and external-directory `make check`" in isolated_redirect_plan
        and "isolated hostile mutations" in isolated_redirect_plan
        and "git diff --check" in isolated_redirect_plan
        and "generated-artifact and likely-secret audits" in isolated_redirect_plan,
        "WatchKit isolated redirect-manager plan must record completed verification",
        failures,
    )
    require_regex(
        interface,
        r"private\s+let\s+alarmRequestTimeout\s*:\s*NSTimeInterval\s*=\s*10\.0",
        "Alarm request timeout must remain an explicit 10-second constant",
        failures,
    )
    require_regex(
        interface,
        r"private\s+let\s+alarmResourceTimeout\s*:\s*NSTimeInterval\s*=\s*15\.0",
        "Alarm resource timeout must remain an explicit 15-second constant",
        failures,
    )
    request_timeout_assignment = (
        "configuration.timeoutIntervalForRequest = alarmRequestTimeout"
    )
    resource_timeout_assignment = (
        "configuration.timeoutIntervalForResource = alarmResourceTimeout"
    )
    manager_construction = "let manager = Manager(configuration: configuration)"
    require_contains(
        interface,
        request_timeout_assignment,
        "Alarm manager configuration must apply the request timeout",
        failures,
    )
    require_contains(
        interface,
        resource_timeout_assignment,
        "Alarm manager configuration must apply the resource timeout",
        failures,
    )
    require(
        interface.find(request_timeout_assignment) < interface.find(manager_construction)
        and interface.find(resource_timeout_assignment) < interface.find(manager_construction),
        "Alarm timeouts must be configured before manager construction",
        failures,
    )
    require(
        "10-second request timeout" in readme
        and "15-second resource timeout" in security
        and "bounded alarm request and resource timeouts" in agents
        and "Bounded alarm submissions" in changes,
        "Repository guidance must document bounded alarm submission timeouts",
        failures,
    )
    require(
        "Status: Completed" in request_timeout_plan
        and "focused portable contract checker" in request_timeout_plan
        and "repository-root and external-directory `make check`" in request_timeout_plan
        and "isolated hostile mutations" in request_timeout_plan
        and "artifact, conflict-marker, large-file, and likely-secret audits"
        in request_timeout_plan,
        "WatchKit alarm request-timeout plan must record completed verification",
        failures,
    )

    if failures:
        print("Alarm WatchKit contract check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Alarm WatchKit contract check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
