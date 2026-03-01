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
- HITL 운영 모델을 단독 연구자 최적화로 경량화:
  - dual lane (`wip` / `record`) 도입
  - 상태/카드 관리는 에이전트 위임
  - 자동화는 compact 3개를 기본으로, legacy 9개는 paused 보존

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
- Follow-up drift audit (2026-03-01):
  - `conda run -n py311 python scripts/hitl_validate_workflow.py` -> pass (`59/59`).
  - `conda run -n py311 python -m pytest -q` -> pass (`11 passed`, warning only).
  - Global skills quick validation (`~/.codex/skills`) -> pass (`21/21`).
  - Repo skills quick validation (`.agents/skills`) -> initially failed (`6/6`, invalid `$` prefix in `name`), then fixed and re-run pass (`6/6`).
  - Markdown hygiene checks:
    - merge conflict markers in `ddpm_project`: none.
    - unmatched fenced code blocks in `ddpm_project` and global `SKILL.md`: none.
    - broken local markdown links in `ddpm_project`: none detected.
- HITL compact model validation (2026-03-01):
  - `conda run --no-capture-output -n py311 python scripts/hitl_validate_workflow.py` -> pass (`78/78`).
  - Added checks:
    - experiment card lane/promotion fields
    - extended state registry columns (`lane,needs_human_action,next_gate`)
    - compact 3 automations + legacy 9 automations presence/paused status
    - `ACTIVE.md` / `INTERFACE.md` section integrity
    - WIP/Record lane policy scenarios
