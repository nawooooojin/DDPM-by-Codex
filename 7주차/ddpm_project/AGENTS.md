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

## Durable Memory Policy
- Maintain `docs/PROMPT.md`, `docs/PLAN.md`, `docs/IMPLEMENT.md`, `docs/STATUS.md`.
