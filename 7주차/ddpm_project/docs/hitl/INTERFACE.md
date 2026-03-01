# HITL Command Interface

## Purpose
Minimize manual YAML/CSV edits.
Humans express intent; agent handles state/card files.

## Supported Commands
- `실험 제안: <idea>`
  - Agent action: create or update draft experiment card.
  - Target state: `DRAFT` or `PLAN_READY`.
- `계획 승인: EXP-...`
  - Agent action: set `PLAN_APPROVED`, prepare run gate draft.
- `실행 승인: EXP-...`
  - Agent action: set `RUN_APPROVED`, start approved command, set `RUNNING`.
- `결과 정리: EXP-...`
  - Agent action: complete result card and move to `RESULT_READY`.
- `머지 승인: EXP-...`
  - Agent action: set `MERGE_APPROVED` and unblock integration.

## Lane Decision Rule
Use `record` lane if any is true:
1. Included in baseline comparison
2. Estimated runtime >= 1 GPU-hour or >= 4 CPU-hours
3. Intended for external sharing/reporting

Otherwise use `wip` lane.

## WIP -> Record Promotion
When user requests promotion:
1. Agent backfills card fields from git diff/log context.
2. Agent writes `promotion_source` and `promotion_reason`.
3. Agent updates `state_index.csv` and `ACTIVE.md`.
