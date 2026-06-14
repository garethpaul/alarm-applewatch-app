.PHONY: lint test build ci verify check

PYTHON ?= python3
override ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

lint:
	$(PYTHON) -m py_compile $(ROOT)scripts/check_alarm_contracts.py

test:
	$(PYTHON) $(ROOT)scripts/check_alarm_contracts.py

build:
	@if command -v xcodebuild >/dev/null 2>&1; then \
		cd $(ROOT) && xcodebuild -workspace Alarm.xcworkspace -scheme Alarm -sdk iphonesimulator CODE_SIGNING_ALLOWED=NO build; \
	else \
		echo "xcodebuild unavailable; skipping legacy Apple build"; \
	fi

ci: lint test

verify: lint test build

check: verify
