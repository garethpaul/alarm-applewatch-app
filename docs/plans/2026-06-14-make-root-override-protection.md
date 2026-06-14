# Make Root Override Protection

Status: Planned

## Problem

The Makefile-derived repository root anchors the portable checker and optional
Xcode workspace build, but a command-line `ROOT` value can replace the ordinary
assignment and redirect verification away from the reviewed checkout.

## Requirements

1. Protect the derived root with GNU Make's `override` directive.
2. Preserve the configurable Python command and all existing targets.
3. Require exact protected-root, Python-override, checker, and rooted Xcode
   execution contracts.
4. Pass local, external-directory, and hostile-root full gates.
5. Reject focused root, tool, path, and completed-plan mutations.

## Verification

- Compile and run the portable checker.
- Run bounded local, external-directory, and hostile `ROOT` `make check`.
- Run focused mutations and plist/XML/workflow audits.
- Audit exact paths, generated artifacts, whitespace, and changed-line
  credentials.
- Record the unavailable Linux `xcodebuild` boundary truthfully.

## Scope Boundaries

- Do not change Swift/Objective-C behavior, dependencies, project metadata,
  workflows, storyboards, or deployment configuration.
- Do not merge or close any pull request without explicit owner authorization.
