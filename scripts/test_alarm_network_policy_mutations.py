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


def mutate_many_and_require_success(label, relative_path, replacements, command):
    with tempfile.TemporaryDirectory(prefix="alarm-policy-mutation-") as temporary:
        checkout = Path(temporary) / "repo"
        copy_repository(checkout)
        path = checkout / relative_path
        content = path.read_text()
        for old, new in replacements:
            if content.count(old) < 1:
                raise AssertionError(f"{label}: mutation target was missing")
            content = content.replace(old, new, 1)
        path.write_text(content)
        result = subprocess.run(
            command,
            cwd=checkout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if result.returncode != 0:
            raise AssertionError(f"{label}: valid mutation failed\n{result.stdout}")


def require_all_mutations_fail(mutations, command):
    survivors = []
    for label, relative_path, old, new in mutations:
        try:
            mutate_and_require_failure(label, relative_path, old, new, command)
        except AssertionError as error:
            survivors.append(str(error))
    if survivors:
        raise AssertionError("\n\n".join(survivors))


def main():
    python = sys.executable
    structural = [python, "scripts/test_alarm_network_policy_contracts.py"]
    repository_contract = [python, "scripts/check_alarm_contracts.py"]
    require_all_mutations_fail(
        [
            (
                "custom shell credential injection",
                ".github/workflows/check.yml",
                """      - name: Run deterministic checks
        run: make ci""",
                """      - name: Run deterministic checks
        env:
          GITHUB_TOKEN: ${{ github.token }}
        shell: bash -c 'git remote set-url origin "https://x-access-token:$GITHUB_TOKEN@github.com/$GITHUB_REPOSITORY"; bash "$1"' -- {0}
        run: make ci""",
            ),
            (
                "native continue on error",
                ".github/workflows/check.yml",
                """      - name: Run native and mutation tests
        run: make native-test mutation-test build""",
                """      - name: Run native and mutation tests
        continue-on-error: true
        run: make native-test mutation-test build""",
            ),
            (
                "native hostile make flags",
                ".github/workflows/check.yml",
                """      - name: Run native and mutation tests
        run: make native-test mutation-test build""",
                """      - name: Run native and mutation tests
        env:
          MAKEFLAGS: -i
        run: make native-test mutation-test build""",
            ),
            (
                "job default shell override",
                ".github/workflows/check.yml",
                """    runs-on: macos-15
    timeout-minutes: 10
    steps:""",
                """    runs-on: macos-15
    timeout-minutes: 10
    defaults:
      run:
        shell: bash {0}
    steps:""",
            ),
            (
                "anchored third checkout",
                ".github/workflows/check.yml",
                """      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0
        with:
          python-version: ${{ matrix.python-version }}
      - name: Run deterministic checks""",
                """      - &checkout-step
        name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0
        with:
          python-version: ${{ matrix.python-version }}
      - *checkout-step
      - name: Run deterministic checks""",
            ),
            (
                "block scalar fake checkout",
                ".github/workflows/check.yml",
                """    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Run native and mutation tests""",
                """    env:
      CHECKOUT_CONTRACT_DECOY: |
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
    steps:
      - name: Run native and mutation tests""",
            ),
            (
                "duplicate top-level permissions",
                ".github/workflows/check.yml",
                """permissions:
  contents: read""",
                """permissions:
  contents: write

permissions:
  contents: read""",
            ),
            (
                "duplicate verification run",
                ".github/workflows/check.yml",
                """      - name: Run deterministic checks
        run: make ci""",
                """      - name: Run deterministic checks
        run: git config --global credential.helper store
        run: make ci""",
            ),
            (
                "duplicate checkout with block",
                ".github/workflows/check.yml",
                """        with:
          persist-credentials: false
      - name: Set up Python""",
                """        with:
          persist-credentials: true
        with:
          persist-credentials: false
      - name: Set up Python""",
            ),
            (
                "duplicate checkout persist credentials",
                ".github/workflows/check.yml",
                """        with:
          persist-credentials: false
      - name: Set up Python""",
                """        with:
          persist-credentials: true
          persist-credentials: false
      - name: Set up Python""",
            ),
            (
                "nested duplicate matrix key",
                ".github/workflows/check.yml",
                """      matrix:
        python-version: ["3.10", "3.12", "3.14"]""",
                """      matrix:
        python-version: ["2.7"]
        python-version: ["3.10", "3.12", "3.14"]""",
            ),
            (
                "undefined alias parser error",
                ".github/workflows/check.yml",
                """      - name: Run native and mutation tests
        run: make native-test mutation-test build""",
                """      - *missing-step""",
            ),
            (
                "malformed flow parser error",
                ".github/workflows/check.yml",
                """permissions:
  contents: read""",
                """permissions: {contents: read""",
            ),
        ],
        repository_contract,
    )
    mutate_many_and_require_success(
        "exact checkout alias",
        ".github/workflows/check.yml",
        [
            (
                """      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Set up Python""",
                """      - &checkout-step
        name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Set up Python""",
            ),
            (
                """      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Run native and mutation tests""",
                """      - *checkout-step
      - name: Run native and mutation tests""",
            ),
        ],
        repository_contract,
    )
    mutate_many_and_require_success(
        "exact checkout input merge",
        ".github/workflows/check.yml",
        [
            (
                """        with:
          persist-credentials: false
      - name: Set up Python""",
                """        with: &checkout-inputs
          persist-credentials: false
      - name: Set up Python""",
            ),
            (
                """        with:
          persist-credentials: false
      - name: Run native and mutation tests""",
                """        with:
          <<: *checkout-inputs
          persist-credentials: false
      - name: Run native and mutation tests""",
            ),
        ],
        repository_contract,
    )
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
        "missing native verification command",
        ".github/workflows/check.yml",
        """      - name: Run native and mutation tests
        run: make native-test mutation-test build""",
        """      # Native verification command removed""",
        repository_contract,
    )
    mutate_and_require_failure(
        "injected credential persistence command",
        ".github/workflows/check.yml",
        """      - name: Run deterministic checks
        run: make ci""",
        """      - name: Run deterministic checks
        run: make ci
      - name: Persist checkout token
        run: git remote set-url origin https://x-access-token:${{ github.token }}@github.com/${{ github.repository }}""",
        repository_contract,
    )
    mutate_and_require_failure(
        "response byte interception",
        "Alarm WatchKit Extension/InterfaceController.swift",
        "manager.delegate.dataTaskDidReceiveData = {",
        "manager.delegate.unreviewedDataCallback = {",
        structural,
    )
    for suffix in ("alt", "arpa", "onion", "example.com", "example.net", "example.org"):
        mutate_and_require_failure(
            f"special-use suffix {suffix}",
            "Alarm WatchKit Extension/AlarmNetworkPolicy.m",
            f'        @"{suffix}",',
            f'        @"removed-{suffix}",',
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
