.PHONY: lint test build verify check

PYTHON ?= python3

lint:
	$(PYTHON) -m py_compile scripts/check_alarm_contracts.py

test:
	$(PYTHON) scripts/check_alarm_contracts.py

build:
	@if command -v xcodebuild >/dev/null 2>&1; then \
		xcodebuild -workspace Alarm.xcworkspace -scheme Alarm -sdk iphonesimulator CODE_SIGNING_ALLOWED=NO build; \
	else \
		echo "xcodebuild unavailable; skipping legacy Apple build"; \
	fi

verify: lint test build

check: verify
