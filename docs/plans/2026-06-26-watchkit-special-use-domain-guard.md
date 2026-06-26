# WatchKit Special-Use Domain Guard

Status: Completed

## Scope

Keep the alarm endpoint's public-DNS-only contract from accepting names in the
IANA Special-Use Domain Names registry.

## Baseline

The native hostname policy rejected local, private, numeric, IDN, and several
reserved suffixes, but still accepted `.alt`, `.arpa`, `.onion`, and the
reserved `example.com`, `example.net`, and `example.org` namespaces. The
focused portable contract failed before implementation on the missing `.alt`
guard.

## Implementation

- Extend the existing delimiter-aware suffix policy with the missing
  special-use namespaces.
- Move accepted native test fixtures from reserved example domains to a normal
  public-DNS-shaped fixture.
- Add native rejection cases for every new namespace.
- Add six hostile mutations that remove each new suffix independently.
- Keep the URL, request, response, timeout, redirect, storage, and DNS-rebinding
  boundaries unchanged.

## Verification

- Focused portable contract and complete portable static checks.
- Six hostile mutations for the new special-use suffixes plus the existing
  mutation suite.
- Repository-root and external-directory `make check` with Ruby 4.0.5.
- hosted macOS native policy gate for the Objective-C behavior tests.
- Python syntax, `git diff --check`, repository integrity, generated-artifact,
  conflict-marker, large-file, and likely-secret audits.

No live endpoint, Watch simulator, paired watch, or physical device is used.
