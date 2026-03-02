# HITL Workflow Operating Guide (Single-Researcher Compact Edition)

This document is the operational policy for running research with Codex under Human-in-the-Loop (HITL).
It is intended to minimize process overhead while preserving reproducibility for official experiments.

## 1) What this guide optimizes for
- Fast iteration for exploratory work.
- Strong control and traceability for reportable results.
- Minimal manual bookkeeping (human approves, agent updates state/cards).

## 2) Core model (dual lane)

## WIP lane
- Purpose: quick probes, shape checks, debugging, rapid coding.
- Gate requirement: none.
- Card requirement: optional.
- Allowed: immediate code/config edits and run execution.
- Constraint: results are not official evidence until promoted.

## Record lane
- Purpose: baseline comparison, externally shared conclusions, merge-critical runs.
- Gate requirement: mandatory.
- Required approvals:
  1. `PLAN_APPROVED`
  2. `RUN_APPROVED`
  3. `MERGE_APPROVED`

## Always true
- Main branch merge requires `MERGE_APPROVED` regardless of lane.

## 3) Hydra switching convention (important)
Lane and experiment are independent axes:
- lane: `lane=wip|record`
- experiment content: `experiment=<name>`

Examples:
```bash
# fast probe
python scripts/train.py lane=wip model.hidden_dim=32

# official tracked run
python scripts/train.py lane=record experiment=paper_repro
```

Do not encode lane semantics into experiment names.
Avoid `+experiment=WIP` style switching.

## 4) Human interface (minimal typing)
Use command-style sentences in chat:
- `실험 제안: <idea>`
- `계획 승인: EXP-...`
- `실행 승인: EXP-...`
- `결과 정리: EXP-...`
- `머지 승인: EXP-...`

Expected behavior:
- Human provides intent/approval.
- Agent drafts and updates cards/state files.

## 5) Source-of-truth files
- `docs/hitl/experiment_card.yaml`
- `docs/hitl/run_gate.yaml`
- `docs/hitl/result_card.yaml`
- `docs/hitl/state_index.csv`
- `docs/hitl/ACTIVE.md`
- `docs/hitl/INTERFACE.md`

## 6) Daily operating SOP

## Start of day
1. Read `docs/hitl/ACTIVE.md`.
2. Confirm top 3 priorities.
3. Approve or reject pending gates.

## During day
1. Use WIP lane for fast technical iteration.
2. Promote to Record lane only when result is comparison-worthy.
3. For Record runs, enforce approval sequence before execution.

## End of day
1. Ensure `ACTIVE.md` is current.
2. Ensure failed runs are triaged (`data|model|config|runtime`).
3. Ensure next human actions are explicit.

## 7) Lane decision rules
Use `record` lane if any condition is true:
1. Included in baseline comparison table.
2. Estimated runtime >= 1 GPU-hour or >= 4 CPU-hours.
3. Intended for external sharing/reporting.

Otherwise default to `wip`.

## 8) WIP -> Record promotion procedure
1. User says promotion intent (example: `이 결과 공식 실험으로 올려`).
2. Agent backfills experiment card from git diff/run metadata.
3. Agent fills `promotion_source` and `promotion_reason`.
4. Agent updates `state_index.csv` and `ACTIVE.md`.
5. Agent moves state to `PLAN_READY`.

This enables “code first, formalize later” without losing reproducibility.

## 9) Approval protocol (Record lane)
1. `PLAN_APPROVED`: plan quality and risk/budget accepted.
2. `RUN_APPROVED`: exact command and expected artifacts accepted.
3. `MERGE_APPROVED`: result interpretation and integration decision accepted.

If approval is missing:
- Agent blocks the step and returns the smallest required next action only.

## 10) Automation policy (compact 3 + legacy paused)
Primary automation set:
1. `daily-hitl-digest` (daily summary)
2. `run-on-approval` (approval-triggered execution helper)
3. `weekly-research-review` (weekly KPI and decisions)

Legacy 9 templates are retained and paused for compatibility.

Alert policy:
- Generate inbox items only when actionable human decisions are needed.
- Avoid non-actionable report spam.

## 11) Context bloat control
Default read set for agent work:
1. `AGENTS.md`
2. `docs/hitl/ACTIVE.md`
3. active card set for current experiment
4. expand to `docs/PLAN.md` or `docs/STATUS.md` only when required

Operational limits:
- Keep max 3 active experiments in `ACTIVE.md`.
- Archive completed cards monthly.
- Keep daily/weekly reports one-page summary first, details as links.

## 12) Required checks
```bash
ruff check .
black --check .
python -m pytest -q
python scripts/toy_sanity_check.py
python scripts/hitl_validate_workflow.py
```

## 13) Definition of done (for Record lane)
A result is done only when all are present:
- exact command
- resolved config snapshot
- commit hash
- artifact/checkpoint reference
- baseline delta and cost context
- clear decision: adopt/hold/drop

## 14) Anti-patterns to block
- running many experiments without state/card trace
- hardcoding run-specific settings in Python
- skipping failure classification
- merging without `MERGE_APPROVED`
- cherry-picking qualitative examples

## 15) Quick examples
```bash
# quick debug in WIP
python scripts/train.py lane=wip runtime.fast_dev_run=true

# formal run in Record lane
python scripts/train.py lane=record experiment=ablation_example
```

```text
실험 제안: hidden_dim 32로 빠르게 검증
계획 승인: EXP-20260301-002
실행 승인: EXP-20260301-002
결과 정리: EXP-20260301-002
머지 승인: EXP-20260301-002
```
