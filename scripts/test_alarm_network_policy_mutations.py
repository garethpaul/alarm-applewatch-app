#!/usr/bin/env python3
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def copy_repository(destination):
    shutil.copytree(
        ROOT,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".git", ".review", "DerivedData", "__pycache__"),
    )


def mutate_and_require_failure(label, relative_path, old, new, command):
    with tempfile.TemporaryDirectory(prefix="alarm-policy-mutation-") as temporary:
        checkout = Path(temporary) / "repo"
        copy_repository(checkout)
        path = checkout / relative_path
        content = path.read_text()
        if content.count(old) < 1:
            raise AssertionError(f"{label}: mutation target was missing")
        path.write_text(content.replace(old, new, 1))
        environment = os.environ.copy()
        environment["ALARM_REPO_ROOT"] = str(checkout)
        result = subprocess.run(
            command,
            cwd=checkout,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if result.returncode == 0:
            raise AssertionError(f"{label}: mutation survived\n{result.stdout}")


def main():
    python = sys.executable
    structural = [python, "scripts/test_alarm_network_policy_contracts.py"]
    repository_contract = [python, "scripts/check_alarm_contracts.py"]
    mutate_and_require_failure(
        "native checkout credential decoy",
        ".github/workflows/check.yml",
        """      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Run native and mutation tests""",
        """      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
      # persist-credentials: false
      - name: Run native and mutation tests""",
        repository_contract,
    )
    mutate_and_require_failure(
        "response byte interception",
        "Alarm WatchKit Extension/InterfaceController.swift",
        "manager.delegate.dataTaskDidReceiveData = {",
        "manager.delegate.unreviewedDataCallback = {",
        structural,
    )
    mutate_and_require_failure(
        "extension source membership",
        "Alarm.xcodeproj/project.pbxproj",
        "\t\t\t\tA18A00011B00000100A1A1A1 /* AlarmNetworkPolicy.m in Sources */,",
        "\t\t\t\t/* AlarmNetworkPolicy.m omitted from Sources */,",
        structural,
    )
    mutate_and_require_failure(
        "bridging header",
        "Alarm.xcodeproj/project.pbxproj",
        "SWIFT_OBJC_BRIDGING_HEADER",
        "REMOVED_BRIDGE_SETTING",
        structural,
    )

    if platform.system() == "Darwin":
        native = ["scripts/run_alarm_network_policy_tests.sh"]
        mutate_and_require_failure(
            "local and private host rejection",
            "Alarm WatchKit Extension/AlarmNetworkPolicy.m",
            "        [self isDisallowedHost:host]) {",
            "        NO) {",
            native,
        )
        mutate_and_require_failure(
            "declared response content type",
            "Alarm WatchKit Extension/AlarmNetworkPolicy.m",
            "            ![mediaType isEqualToString:@\"text/plain\"]) {",
            "            ![mediaType isEqualToString:@\"text/plain\"] && NO) {",
            native,
        )
        mutate_and_require_failure(
            "response body cap",
            "Alarm WatchKit Extension/AlarmNetworkPolicy.m",
            "NSUInteger const AlarmMaximumResponseBodyBytes = 4096;",
            "NSUInteger const AlarmMaximumResponseBodyBytes = 65536;",
            native,
        )
        mutate_and_require_failure(
            "inclusive body boundary",
            "Alarm WatchKit Extension/AlarmNetworkPolicy.m",
            "if ([data length] > AlarmMaximumResponseBodyBytes - received)",
            "if ([data length] >= AlarmMaximumResponseBodyBytes - received)",
            native,
        )

    print("Alarm network policy mutation tests passed.")


if __name__ == "__main__":
    main()
