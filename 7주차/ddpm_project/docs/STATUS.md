# STATUS

## Current State
- Integrated repository scaffold and durable memory into `7주차/ddpm_project`.
- Preserved existing DDPM training/evaluation pipeline.
- Added toy Lightning pipeline with Hydra config and sanity scripts.
- Added HITL contract files under `docs/hitl` and HITL report channels under `reports/hitl`.

## Decisions
- Existing DDPM entrypoints/config retained to avoid regression.
- New scaffold integrated with `toy_` prefixes where collisions existed.
- Agent policy/docs/skills/safety files now live in `ddpm_project`.
- HITL control model fixed to 3 gates: `PLAN_APPROVED`, `RUN_APPROVED`, `MERGE_APPROVED`.

## How To Run
- DDPM: `python scripts/train.py`
- Toy: `python scripts/toy_train.py`
- Toy sanity: `python scripts/toy_sanity_check.py`

## Known Issues
- Commands requiring `hydra`, `torch`, `lightning` fail unless environment dependencies are installed.
- In this Codex sandbox runtime, `torch` import may abort with `OMP: Error #179: Can't open SHM2` when running full model tests/sanity scripts.

## Validation Log
- Syntax smoke: `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m compileall -q src scripts tests`.
- Runtime smoke dependency error expected in clean environment.
- Skill frontmatter validation: `rg "name:|description:" .agents/skills/**/SKILL.md`.
- Safety rule section validation: `rg "forbidden|prompt|allow" codex/rules/default.rules`.
- Runtime check attempt: `python3 scripts/toy_train.py trainer.fast_dev_run=true` -> `ModuleNotFoundError: No module named 'hydra'`.
- HITL workflow validation: `conda run --no-capture-output -n py311 python scripts/hitl_validate_workflow.py`.
  - Result: `59/59` checks passed.
  - Report: `reports/hitl/validation_report_2026-03-01.md`.
- Additional runtime attempts (environment issue reproduction):
  - `conda run --no-capture-output -n py311 python -m pytest -q` -> abort (`OMP #179`).
  - `conda run --no-capture-output -n py311 python scripts/toy_sanity_check.py` -> abort (`OMP #179`).
