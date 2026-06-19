#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BUILD_DIR=$(mktemp -d "${TMPDIR:-/tmp}/alarm-network-policy.XXXXXX")
trap 'rm -rf "$BUILD_DIR"' EXIT HUP INT TERM

clang \
  -fobjc-arc \
  -fmodules \
  -Wall \
  -Wextra \
  -Werror \
  -framework Foundation \
  "$ROOT/Alarm WatchKit Extension/AlarmNetworkPolicy.m" \
  "$ROOT/scripts/test_alarm_network_policy.m" \
  -o "$BUILD_DIR/test_alarm_network_policy"

"$BUILD_DIR/test_alarm_network_policy"
