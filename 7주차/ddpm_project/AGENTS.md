# AGENTS Working Agreements

This repository hosts two tracks:
- DDPM CIFAR10 pipeline (`scripts/train.py`, `scripts/eval.py`)
- Toy Lightning sanity pipeline (`scripts/toy_*.py`)

## Core Rules
- No hardcoded hyperparameters or paths in Python code.
- All knobs must be configurable through Hydra YAML.
- Keep each change set small and reviewable.
- Run milestone validation commands and stop/fix on failure.
- Add new experiments via `configs/experiment/*.yaml`.

## Dual-Lane HITL Policy (Default)

### 1) WIP lane (fast exploration)
- Purpose: quick hypothesis checks, shape/debug iterations, rapid coding.
- Card requirement: optional.
- Gate requirement: exempt.
- Allowed:
  - immediate code/config edits
  - immediate run execution
- Restriction:
  - WIP results are not official comparison artifacts until promoted.

### 2) Record lane (official experiment)
- Purpose: baseline comparison, reportable outcomes, shareable results.
- Card requirement: mandatory.
- Gate requirement: mandatory.
- Required approvals:
  1. `PLAN_APPROVED`
  2. `RUN_APPROVED`
  3. `MERGE_APPROVED`

### 3) Branch integration rule
- Merge to main branch always requires `MERGE_APPROVED` (lane-independent).

## State / Card Ownership
- Human gives approval intent only (Y/N semantics via command phrases).
- Agent owns card creation/update, state transitions, and `docs/hitl/ACTIVE.md` sync.
- Manual edits are allowed; latest synchronized agent state is treated as source of truth.

## Human Command Interface
- `실험 제안: <idea>`
- `계획 승인: EXP-...`
- `실행 승인: EXP-...`
- `결과 정리: EXP-...`
- `머지 승인: EXP-...`

## Manual-First Flexibility Rule
- Users can code/run first.
- If later promoted to Record lane, agent backfills cards and state from git diff/log context.

## Architecture Rules
- `src/` contains reusable package code only.
- `scripts/` are orchestration-only entrypoints.
- `tests/` cover shape/io/smoke/config composition.
- `outputs/` stores run artifacts and is not committed.

## Mandatory Sanity Protocol
1. Initial loss sanity
2. Overfit one batch
3. Fast dev run smoke

## Quality Gates
- `ruff check .`
- `black --check .`
- `python -m pytest -q`

## Dependency Policy
- Any new dependency requires explicit user confirmation.

## Context Hygiene Policy
- Default read set:
  1. `AGENTS.md`
  2. `docs/hitl/ACTIVE.md`
  3. active experiment card (1 set)
  4. expand to `docs/PLAN.md` / `docs/STATUS.md` only when needed
- Keep at most 3 active experiments in `ACTIVE.md`.

## Durable Memory Policy
- Maintain `docs/PROMPT.md`, `docs/PLAN.md`, `docs/IMPLEMENT.md`, `docs/STATUS.md`.
- Maintain HITL contract files under `docs/hitl/` and report streams under `reports/hitl/`.
