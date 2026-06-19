# Security Policy

## Supported Versions

The supported security scope for `alarm-applewatch-app` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: AppleWatch Alarm App

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/alarm-applewatch-app` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be an Apple platform application or Swift sample. The active security scope is the code and documentation on the default branch.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found database, model, query, or persistence-related code; changes in those areas should receive security-focused review before merge.
- Dependency manifests detected: Podfile, Podfile.lock. Dependency updates should preserve lockfiles when present and avoid introducing packages without a clear maintenance reason.
- Alarm endpoint configuration should remain HTTPS, use no explicit port, stay
  credential-free, and remain scoped to the explicit `/alarm` path.
- Alarm-hour inputs must be bounded while still represented as floats so
  non-finite or extreme values cannot trap during integer conversion.
- The reserved alarm placeholder comparison is case-insensitive and ignores a
  trailing root dot so DNS-equivalent `example.invalid` hosts cannot enable the
  request path.
- The reserved placeholder domain includes `example.invalid` and its
  dot-delimited subdomains; deceptive near matches are not classified by a
  delimiter-free suffix check.
- Alarm submissions use POST to keep the normalized `alarmTime` out of request
  URLs and the proxy, server, analytics, or diagnostic logs that retain them.
- Alarm submissions reject redirect follow-up requests through a dedicated
  Alamofire manager without mutating the process-wide shared manager.
- Alarm submissions use a 10-second request timeout and 15-second resource timeout
  so a stalled endpoint cannot retain the watch request indefinitely.
- Alarm submissions use an ephemeral session so cookies, credentials, and cache data are not persisted.
- Alarm submissions disable cookie, credential, and cache stores so one request cannot influence the next.
- Alarm endpoint validation accepts only canonical ASCII public-DNS-shaped
  hosts and rejects IP literals, legacy numeric IPv4 forms, IDN/punycode,
  localhost, local/reserved suffixes, and encoded path ambiguity.
- Alarm responses must stay on the validated URL, return 2xx, use an allowed
  declared media type, and remain within the 4096-byte streamed body limit.
  Response bytes are discarded rather than retained by Alamofire.
- URL validation does not pin DNS answers. A trusted hostname can still resolve
  or rebind to a private address after validation, so production use requires an
  authorized static endpoint plus DNS and egress controls.
- Response validation emits only a generic alarm submission failure for the
  still-current request; stale callbacks and dependency details are ignored.
- The parsed endpoint scheme is compared case-insensitively; raw string prefixes
  must not replace the parsed HTTPS-only transport boundary.

## Mobile Privacy Notes

If this project requests device permissions such as location, camera, microphone, contacts, Bluetooth, health data, or local storage access, reports should describe the permission involved and whether sensitive data can be accessed, persisted, or transmitted unexpectedly. Please avoid testing against real third-party user data or accounts you do not control.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
