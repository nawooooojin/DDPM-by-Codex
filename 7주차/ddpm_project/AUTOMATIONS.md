# Codex Automations Prompt Pack (HITL Compact Mode)

Default policy:
- All automations start in `PAUSED`.
- Approval surface is Codex inbox.
- Record lane run execution requires `RUN_APPROVED`.
- Inbox creation is suppressed unless actionable items exist.

## Compact Set (Primary: 3 automations)

## 1) Daily HITL Digest
- Name: `daily-hitl-digest`
- Suggested schedule: Every day at 09:00
- Prompt:
  - Aggregate lint/tests/sanity summary, 24h code delta, and latest failed-run triage into one report.
  - Write output to `reports/hitl/daily.md`.
  - Create inbox item only when actionable fixes or approvals are required.

## 2) Run On Approval
- Name: `run-on-approval`
- Suggested schedule: Event-driven / on-demand trigger
- Prompt:
  - Trigger only for `RUN_APPROVED` commands.
  - Start the approved command, set state to `RUNNING`, and draft `RESULT_READY` summary on completion.
  - Do not mutate unrelated files.

## 3) Weekly Research Review
- Name: `weekly-research-review`
- Suggested schedule: Every Monday at 09:00
- Prompt:
  - Update `reports/hitl/weekly.md` with KPI trends, failure patterns, reproducibility gaps, and next-week priorities.
  - Keep it to one-page summary and link detailed logs.

## Legacy Templates (Preserved, PAUSED)
These are retained for compatibility and can stay paused unless explicitly needed:
- `nightly-health-check`
- `daily-code-delta`
- `daily-hitl-queue-build`
- `run-gate-preflight`
- `run-monitor`
- `failed-run-triage`
- `weekly-experiment-digest`
- `prompt-plan-drift-check`
- `repro-audit`

## Activation Guidance
1. Start with `daily-hitl-digest` only.
2. Enable `weekly-research-review` after 3-5 successful experiment cycles.
3. Use `run-on-approval` when state transition discipline is stable.
