# HITL Workflow (Single-Researcher Compact Edition)

## 1) Why this version
The original full HITL stack improved control but added friction for solo research.
This compact edition keeps reproducibility for official experiments while restoring rapid exploration speed.

## 2) Default operating model
- Dual lane:
  - `wip`: fast exploration (no mandatory gate)
  - `record`: official experiment (3-gate required)
- Human responsibilities:
  - give approval intent and final decisions
- Agent responsibilities:
  - draft/update cards
  - transition state
  - sync `docs/hitl/ACTIVE.md`

## 3) Gate scope
- `wip` lane: gate-exempt for mutation/run.
- `record` lane:
  1. `PLAN_APPROVED`
  2. `RUN_APPROVED`
  3. `MERGE_APPROVED`
- Main branch merge always needs `MERGE_APPROVED`.

## 4) Minimal context set
Default read set for agent operations:
1. `AGENTS.md`
2. `docs/hitl/ACTIVE.md`
3. active experiment card (single set)
4. expand to `docs/PLAN.md` / `docs/STATUS.md` only when needed

## 5) Source-of-truth files
- `docs/hitl/experiment_card.yaml`
- `docs/hitl/run_gate.yaml`
- `docs/hitl/result_card.yaml`
- `docs/hitl/state_index.csv`
- `docs/hitl/ACTIVE.md`
- `docs/hitl/INTERFACE.md`

## 6) Human command interface
- `실험 제안: hidden_dim 32 테스트`
- `계획 승인: EXP-20260301-001`
- `실행 승인: EXP-20260301-001`
- `결과 정리: EXP-20260301-001`
- `머지 승인: EXP-20260301-001`

Humans should not manually edit YAML/CSV in normal flow.
Manual edits are allowed, but agent-synchronized state is canonical.

## 7) Lane decision rules
Use `record` lane if any are true:
1. baseline comparison target
2. estimated runtime >= 1 GPU-hour or >= 4 CPU-hours
3. external sharing/reporting target

Otherwise use `wip`.

## 8) WIP -> Record promotion
Supported path:
1. user explores quickly in WIP
2. user requests promotion
3. agent backfills record card from git diff/run context
4. state moves to `PLAN_READY` with `promotion_source/promotion_reason` filled

## 9) Automation set (compact 3)
Primary:
1. `daily-hitl-digest` (daily 09:00)
2. `run-on-approval` (event-driven / on-demand)
3. `weekly-research-review` (weekly Monday 09:00)

Legacy 9 templates remain paused for compatibility.

## 10) Validation
```bash
conda run --no-capture-output -n py311 python scripts/hitl_validate_workflow.py
```

Checks include:
- schema fields (`lane`, promotion metadata, extended state columns)
- state transition safety
- compact+legacy automation presence and paused status
- context hub file presence

## 11) Practical defaults
- Keep at most 3 active experiments in `ACTIVE.md`.
- Archive completed cards monthly.
- Daily/weekly reports are one-page summary first, details by links.
