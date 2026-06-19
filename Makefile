.PHONY: lint test native-test mutation-test build ci verify check

PYTHON ?= python3
override ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

lint:
	$(PYTHON) -m py_compile $(ROOT)scripts/check_alarm_contracts.py $(ROOT)scripts/test_alarm_network_policy_contracts.py $(ROOT)scripts/test_alarm_network_policy_mutations.py

test:
	$(PYTHON) $(ROOT)scripts/check_alarm_contracts.py
	$(PYTHON) $(ROOT)scripts/test_alarm_network_policy_contracts.py

native-test:
	@if [ "$$(uname -s)" = Darwin ] && command -v clang >/dev/null 2>&1; then \
		$(ROOT)scripts/run_alarm_network_policy_tests.sh; \
	else \
		echo "Apple Foundation toolchain unavailable; skipping native policy tests"; \
	fi

mutation-test:
	$(PYTHON) $(ROOT)scripts/test_alarm_network_policy_mutations.py

build:
	@if command -v xcodebuild >/dev/null 2>&1; then \
		cd $(ROOT) && xcodebuild -list -workspace Alarm.xcworkspace >/dev/null; \
		if [ "$${RUN_LEGACY_XCODE_BUILD:-0}" = 1 ]; then \
			cd $(ROOT) && xcodebuild -workspace Alarm.xcworkspace -scheme Alarm -sdk iphonesimulator CODE_SIGNING_ALLOWED=NO build; \
		else \
			echo "Legacy WatchKit 1 / Swift 1 build not executed; set RUN_LEGACY_XCODE_BUILD=1 with a compatible Xcode 6 toolchain"; \
		fi; \
	else \
		echo "xcodebuild unavailable; legacy Apple project parsing not executed"; \
	fi

ci: lint test mutation-test

verify: lint test mutation-test native-test build

check: verify
