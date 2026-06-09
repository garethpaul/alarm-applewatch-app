#!/usr/bin/env python3
"""Static contracts for the legacy Alarm WatchKit sample."""

import json
from pathlib import Path
import plistlib
import re
import sys
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "Alarm.xcworkspace/contents.xcworkspacedata",
    "Alarm.xcodeproj/project.pbxproj",
    "Alarm/Info.plist",
    "Alarm WatchKit App/Info.plist",
    "Alarm WatchKit Extension/Info.plist",
    "Alarm WatchKit Extension/InterfaceController.swift",
    "Alarm WatchKit Extension/NotificationController.swift",
    "Alarm WatchKit Extension/PushNotificationPayload.apns",
    "Alarm WatchKit App/Base.lproj/Interface.storyboard",
    "AlarmTests/AlarmTests.swift",
    "AlarmTests/Info.plist",
    "Podfile",
    "Podfile.lock",
    "README.md",
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


def check_alarm_endpoint(interface, extension_plist, failures):
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
    require_contains(
        interface,
        "stringByTrimmingCharactersInSet",
        "alarm endpoint must be trimmed before validation",
        failures,
    )
    require_contains(
        interface,
        'hasPrefix("https://")',
        "InterfaceController must require HTTPS alarm endpoints",
        failures,
    )
    require_contains(
        interface,
        "NSURL(string: trimmedEndpoint)",
        "InterfaceController must parse AlarmEndpointURL before using it",
        failures,
    )
    require_contains(
        interface,
        "url.host",
        "InterfaceController must require a host on AlarmEndpointURL",
        failures,
    )
    require_contains(
        interface,
        "if let endpoint = alarmEndpointURL()",
        "setAlarm must skip network requests when the endpoint is not configured",
        failures,
    )
    require_contains(
        interface,
        "Alamofire.request(.GET, endpoint, parameters: alarmParameters())",
        "alarm request must use the validated endpoint and parameter helper",
        failures,
    )
    require(
        not re.search(r"Alamofire\.request\(\s*\.GET\s*,\s*\"", interface),
        "alarm request must not inline a URL literal",
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


def check_docs(readme, changes, plan, failures):
    require_contains(readme, "Alarm.xcworkspace", "README must direct maintainers to open the workspace", failures)
    require_contains(readme, "make check", "README must document local verification", failures)
    require_contains(readme, "AlarmEndpointURL", "README must document endpoint configuration", failures)
    require_contains(changes, "static contracts", "CHANGES must mention static contract coverage", failures)
    require_contains(plan, "AlarmEndpointURL", "endpoint plan must document the plist-backed endpoint", failures)


def main():
    failures = []

    check_required_files(failures)

    interface = read_text("Alarm WatchKit Extension/InterfaceController.swift", failures)
    storyboard = read_text("Alarm WatchKit App/Base.lproj/Interface.storyboard", failures)
    project = read_text("Alarm.xcodeproj/project.pbxproj", failures)
    podfile = read_text("Podfile", failures)
    podfile_lock = read_text("Podfile.lock", failures)
    readme = read_text("README.md", failures)
    changes = read_text("CHANGES.md", failures)
    plan = read_text("docs/plans/2026-06-08-watchkit-endpoint-contracts.md", failures)

    app = read_plist("Alarm/Info.plist", failures)
    watch_app = read_plist("Alarm WatchKit App/Info.plist", failures)
    extension = read_plist("Alarm WatchKit Extension/Info.plist", failures)
    tests = read_plist("AlarmTests/Info.plist", failures)

    check_alarm_endpoint(interface, extension, failures)
    check_alarm_hour_bounds(interface, storyboard, failures)
    check_watchkit_outlet_safety(interface, failures)
    check_plist_contracts(app, watch_app, extension, tests, failures)
    check_push_payload(failures)
    check_dependency_and_project_contracts(project, podfile, podfile_lock, failures)
    check_docs(readme, changes, plan, failures)

    if failures:
        print("Alarm WatchKit contract check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Alarm WatchKit contract check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
