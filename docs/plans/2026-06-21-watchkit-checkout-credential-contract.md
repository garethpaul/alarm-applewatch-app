# WatchKit Checkout Credential Contract

Status: Completed

## Scope

Ensure both Linux static verification and macOS native-policy jobs bind
credential isolation to their own immutable checkout steps.

## Baseline

The workflow correctly disabled persisted credentials twice, but the static
checker inspected only the first checkout block. Removing the native job's
`with` block and adding a decoy `persist-credentials: false` comment still
passed every existing checkout contract.

## Implementation

- Extract every matching checkout action block instead of returning the first.
- Require both reviewed checkout blocks to contain the adjacent disabled
  credential setting.
- Require exactly the reviewed portable and native verification commands so a
  checkout-only job or injected credential command cannot satisfy the static
  contract.
- Add the reproduced native-job decoy as a permanent hostile mutation.
- Add native-command removal and injected-command attacks as permanent hostile
  mutations.
- Document the stronger two-step ownership boundary.

## Verification

- Repository-root and external-directory `make check`.
- Hostile `ROOT` invocation of the portable CI target.
- The pre-change native checkout decoy reproduction passes the old contract and
  fails the strengthened checker at the intended checkout-step assertion.
- Removing the native command and injecting an additional credential command
  both fail at the exact workflow-command assertion.
- `git diff --check`, strict repository integrity checks, and changed-file
  credential-shape scanning.
