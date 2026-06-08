#!/usr/bin/env python3
"""Static contracts for the legacy Alarm WatchKit sample."""

from pathlib import Path
import plistlib
import sys


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_plist(relative_path, failures):
    try:
        with (ROOT / relative_path).open("rb") as plist_file:
            return plistlib.load(plist_file)
    except Exception as exc:
        failures.append(f"{relative_path} is not readable as a plist: {exc}")
        return {}


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def main():
    failures = []

    interface = read_text("Alarm WatchKit Extension/InterfaceController.swift")
    extension_plist = read_plist("Alarm WatchKit Extension/Info.plist", failures)
    project = read_text("Alarm.xcodeproj/project.pbxproj")

    endpoint = extension_plist.get("AlarmEndpointURL")

    require(
        "http://myhome.com/alarm" not in interface,
        "alarm endpoint must not be hardcoded as a plain HTTP source value",
        failures,
    )
    require(
        'objectForInfoDictionaryKey("AlarmEndpointURL")' in interface,
        "InterfaceController must read AlarmEndpointURL from extension Info.plist",
        failures,
    )
    require(
        'hasPrefix("https://")' in interface,
        "InterfaceController must require HTTPS alarm endpoints",
        failures,
    )
    require(
        "if let endpoint = alarmEndpointURL()" in interface,
        "setAlarm must skip network requests when the endpoint is not configured",
        failures,
    )
    require(
        "alarmParameters()" in interface and "alarmTime" in interface,
        "alarm request parameters must stay explicit and testable",
        failures,
    )
    require(
        isinstance(endpoint, str) and endpoint.startswith("https://"),
        "extension Info.plist must define an HTTPS AlarmEndpointURL placeholder",
        failures,
    )
    require(
        "NSAllowsArbitraryLoads" not in read_text("Alarm/Info.plist")
        and "NSAllowsArbitraryLoads" not in read_text("Alarm WatchKit App/Info.plist")
        and "NSAllowsArbitraryLoads" not in read_text("Alarm WatchKit Extension/Info.plist"),
        "app plists must not enable arbitrary App Transport Security loads",
        failures,
    )
    require(
        "Alarm.xcworkspace" in read_text("README.md"),
        "README must direct maintainers to open the workspace",
        failures,
    )
    require(
        "INFOPLIST_FILE = \"Alarm WatchKit Extension/Info.plist\";" in project,
        "Xcode project must keep the WatchKit extension plist wired",
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
