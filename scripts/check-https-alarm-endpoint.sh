#!/usr/bin/env bash
set -euo pipefail

source_file="Alarm WatchKit Extension/InterfaceController.swift"

grep -q 'private let alarmEndpointURL = "https://myhome.com/alarm"' "$source_file"
grep -q 'private let alarmTimeParameter = "alarmTime"' "$source_file"
grep -q 'Alamofire.request(.GET, alarmEndpointURL' "$source_file"

if grep -RIn --include='*.swift' 'http://myhome.com/alarm' .; then
  echo "Alarm endpoint must not use cleartext HTTP" >&2
  exit 1
fi
