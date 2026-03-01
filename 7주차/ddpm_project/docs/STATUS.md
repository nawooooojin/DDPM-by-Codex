# STATUS

## Current State
- Integrated repository scaffold and durable memory into `7주차/ddpm_project`.
- Preserved existing DDPM training/evaluation pipeline.
- Added toy Lightning pipeline with Hydra config and sanity scripts.

## Decisions
- Existing DDPM entrypoints/config retained to avoid regression.
- New scaffold integrated with `toy_` prefixes where collisions existed.
- Agent policy/docs/skills/safety files now live in `ddpm_project`.

## How To Run
- DDPM: `python scripts/train.py`
- Toy: `python scripts/toy_train.py`
- Toy sanity: `python scripts/toy_sanity_check.py`

## Known Issues
- Commands requiring `hydra`, `torch`, `lightning` fail unless environment dependencies are installed.

## Validation Log
- Syntax smoke: `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m compileall -q src scripts tests`.
- Runtime smoke dependency error expected in clean environment.
- Skill frontmatter validation: `rg "name:|description:" .agents/skills/**/SKILL.md`.
- Safety rule section validation: `rg "forbidden|prompt|allow" codex/rules/default.rules`.
- Runtime check attempt: `python3 scripts/toy_train.py trainer.fast_dev_run=true` -> `ModuleNotFoundError: No module named 'hydra'`.
