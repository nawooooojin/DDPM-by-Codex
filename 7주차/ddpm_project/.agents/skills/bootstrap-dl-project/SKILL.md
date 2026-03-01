---
name: "$bootstrap-dl-project"
description: "새 프로젝트/새 브랜치에서 스캐폴딩 점검, configs/src/scripts/tests 규칙 준수 여부 검사 및 자동 수정"
---

# $bootstrap-dl-project

## Purpose
Validate scaffold consistency for this repo.

## Checks
1. Required directories exist.
2. Package dirs contain `__init__.py`.
3. Hydra defaults composition is valid.
4. Scripts are orchestration-only.
5. Tests include shape/io/config smoke.

## Validation
- `ruff check .`
- `black --check .`
- `python -m pytest -q`
