# Codex Automations Prompt Pack

## 1) Nightly Health
- Name: Nightly Lint + Tests + Sanity
- Suggested schedule: Every night at 1:00 AM local time
- Prompt: Run `ruff check .`, `black --check .`, and `python -m pytest -q`; then run `$sanity-check` and summarize pass/fail, first failure root cause, and fix order.

## 2) Weekly Experiment Digest
- Name: Weekly Experiment Table Refresh
- Suggested schedule: Every Monday at 9:00 AM local time
- Prompt: Use `$summarize-results` to parse recent runs and refresh `reports/weekly.md` with run path, key overrides, and metrics.

## 3) Daily Code Change Digest
- Name: Daily Code Delta by Directory
- Suggested schedule: Every day at 6:00 PM local time
- Prompt: Summarize last 24h git changes grouped by `src/`, `configs/`, `scripts/`, `tests/`, `docs/`; highlight untested changes.

## 4) On-Demand Failure Triage
- Name: Triage Latest Failed Run
- Suggested schedule: Manual / on-demand
- Prompt: Inspect latest failed run under `outputs/`, classify root cause (data/model/config/runtime), and propose smallest safe patch.

## 5) Drift Check
- Name: Prompt-Plan-Code Drift Check
- Suggested schedule: Every weekday at 10:00 AM local time
- Prompt: Compare `docs/PROMPT.md` and `docs/PLAN.md` against current code/tests and list mismatches with concrete update actions.
