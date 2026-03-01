# PLAN

## M1. Structure and Policy
- Acceptance: `pyproject.toml`, `.gitignore`, docs/skills/rules present.
- Validate: `rg "name:|description:" .agents/skills/**/SKILL.md`

## M2. Code Integration
- Acceptance: existing DDPM code remains; toy modules/scripts added.
- Validate: syntax compile for `src`, `scripts`, `tests`.

## M3. Config Integration
- Acceptance: DDPM `configs/train.yaml` unchanged; toy config added as `configs/train_toy.yaml`.
- Validate: compose tests for toy experiment files.

## M4. Sanity Workflow
- Acceptance: three sanity checks available through `scripts/toy_sanity_check.py`.
- Validate: command execution once dependencies are installed.

## Stop-and-Fix
- On any failed validation, pause and record root cause + fix in `docs/STATUS.md`.
