# Codex Automations Prompt Pack (HITL Standard)

Default policy:
- All automations start in `PAUSED`.
- Approval surface is Codex inbox.
- No run execution unless state is `RUN_APPROVED`.

## 1) Nightly Health Check
- Name: Nightly Health Check
- Suggested schedule: Every day at 01:00
- Prompt: Run lint/tests/sanity checks and write PASS/FAIL summary plus first failing cause to `reports/hitl/inbox/`.

## 2) Daily Code Delta
- Name: Daily Code Delta
- Suggested schedule: Every day at 18:00
- Prompt: Summarize 24h code changes by directory, flag risky/untested changes, and output follow-up checks.

## 3) Daily HITL Queue Build
- Name: Daily HITL Queue Build
- Suggested schedule: Every day at 09:00
- Prompt: Draft PLAN_READY experiment cards from backlog hypotheses using `docs/hitl/experiment_card.yaml`.

## 4) Run Gate Preflight
- Name: Run Gate Preflight
- Suggested schedule: Weekdays hourly
- Prompt: For `PLAN_APPROVED` items, generate RUN_READY gate cards with command, budget, artifacts, rollback plan.

## 5) Run Monitor
- Name: Run Monitor
- Suggested schedule: Every 2 hours
- Prompt: Monitor RUNNING jobs and emit alerts/triage drafts without mutating code.

## 6) Failed Run Triage
- Name: Failed Run Triage
- Suggested schedule: Every day at 11:00
- Prompt: Classify most recent failure (data/model/config/runtime), create minimal repro command, suggest smallest safe fix.

## 7) Weekly Experiment Digest
- Name: Weekly Experiment Digest
- Suggested schedule: Every Monday at 09:00
- Prompt: Update `reports/hitl/weekly.md` with metric trends, config deltas, cost signals, and prioritized next steps.

## 8) Prompt Plan Drift Check
- Name: Prompt Plan Drift Check
- Suggested schedule: Weekdays at 10:00
- Prompt: Compare `docs/PROMPT.md`/`docs/PLAN.md` vs code/tests/run state and report mismatches.

## 9) Repro Audit
- Name: Repro Audit
- Suggested schedule: Every Friday at 16:00
- Prompt: Audit top runs for reproducibility completeness (config, commit, checkpoint, data ref, rerun command).
