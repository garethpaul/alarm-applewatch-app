#!/usr/bin/env python3
import os
from pathlib import Path


ROOT = Path(os.environ.get("ALARM_REPO_ROOT", Path(__file__).resolve().parents[1]))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    header = (ROOT / "Alarm WatchKit Extension/AlarmNetworkPolicy.h").read_text()
    implementation = (ROOT / "Alarm WatchKit Extension/AlarmNetworkPolicy.m").read_text()
    interface = (ROOT / "Alarm WatchKit Extension/InterfaceController.swift").read_text()
    project = (ROOT / "Alarm.xcodeproj/project.pbxproj").read_text()
    makefile = (ROOT / "Makefile").read_text()
    workflow = (ROOT / ".github/workflows/check.yml").read_text()
    readme = (ROOT / "README.md").read_text()
    security = (ROOT / "SECURITY.md").read_text()
    plan = (ROOT / "docs/plans/2026-06-19-watchkit-network-boundary-review.md").read_text()

    require("AlarmMaximumResponseBodyBytes" in header, "response bound must be public")
    require("validatedEndpointURL" in implementation, "endpoint policy must be native")
    require("NSASCIIStringEncoding" in implementation, "IDN input must fail closed")
    require("isDisallowedHost" in implementation, "private/local hosts must be rejected")
    require("percentEncodedPath" in implementation, "encoded path ambiguity must be rejected")
    require("isAcceptableResponse" in implementation, "response metadata must be validated")
    require("allHeaderFields" in implementation and "valueForHTTPHeaderField" not in implementation,
            "response header validation must remain compatible with iOS 8")
    require("shouldCancelTask" in implementation, "streamed response bytes must be bounded")
    require("AlarmNetworkPolicy.validatedEndpointURL" in interface, "WatchKit must use native URL policy")
    require("dataTaskDidReceiveResponse" in interface, "WatchKit must gate response metadata")
    require("dataTaskDidReceiveData" in interface, "WatchKit must intercept response bytes")
    require("shouldCancelTask" in interface, "WatchKit must cancel oversized responses")
    require("A18A00011B00000100A1A1A1 /* AlarmNetworkPolicy.m in Sources */," in project,
            "native policy must belong to extension target sources phase")
    require(project.count("SWIFT_OBJC_BRIDGING_HEADER") == 2,
            "both extension configurations must import native policy")
    require("RUN_LEGACY_XCODE_BUILD" in makefile, "legacy Xcode build must be explicit opt-in")
    require("test_alarm_network_policy_mutations.py" in makefile, "mutation tests must run locally and in CI")
    require("native-policy:" in workflow and "runs-on: macos-15" in workflow,
            "hosted native policy tests must run on macOS")
    require("make native-test" in workflow, "hosted macOS job must execute native tests")
    require("DNS answers are not pinned" in readme and "DNS answers" in security,
            "DNS and rebinding limitations must remain explicit")
    require("Status: Completed" in plan and "Seven hostile mutations" in plan,
            "network boundary review plan must record completed evidence")
    print("Alarm network policy structural tests passed.")


if __name__ == "__main__":
    main()
