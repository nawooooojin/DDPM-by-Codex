# HITL Workflow (Dual-Lane)

## Lanes
- `wip`: fast exploration. No gate requirement.
- `record`: official experiment. 3-gate required.

## Canonical States (Record lane)
- DRAFT
- PLAN_READY
- PLAN_APPROVED
- RUN_READY
- RUN_APPROVED
- RUNNING
- RESULT_READY
- MERGE_APPROVED
- MERGED / REJECTED

## Gate Rules
- `wip` lane: gate-exempt for mutation/run.
- `record` lane:
  1. `PLAN_APPROVED` before official mutation for the experiment.
  2. `RUN_APPROVED` before official run execution.
  3. `MERGE_APPROVED` before branch integration.
- Main branch merge always requires `MERGE_APPROVED`.

## Source-of-Truth Files
- `experiment_card.yaml`
- `run_gate.yaml`
- `result_card.yaml`
- `state_index.csv`
- `ACTIVE.md` (single context hub)

## Human Interface
- `실험 제안: <idea>`
- `계획 승인: EXP-...`
- `실행 승인: EXP-...`
- `결과 정리: EXP-...`
- `머지 승인: EXP-...`

## Ownership Model
- Human: approval intent and final decisions.
- Agent: card drafting, state transitions, `ACTIVE.md` sync.
