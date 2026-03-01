# DDPM Research Artifact (Hydra)

This repo now includes:
- DDPM CIFAR-10 training/evaluation pipeline (existing)
- Toy Lightning pipeline for reproducibility/sanity protocol (new)
- Durable project memory and repo-scoped Codex skills (new)

## 1) Install

```bash
cd "7주차/ddpm_project"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Optional modern setup
pip install -e .
pip install -e .[dev]
```

## 2) DDPM Train/Eval (existing)

```bash
python scripts/train.py logging.use_wandb=true
python scripts/eval.py runtime.checkpoint_path=/absolute/path/to/last.pt logging.use_wandb=false
```

DDPM quick checks:

```bash
python scripts/train.py runtime.fast_dev_run=true logging.use_wandb=false
python scripts/train.py runtime.overfit_one_batch=true runtime.total_steps=1000 logging.use_wandb=false
python scripts/train.py experiment=ddpm_test
```

이미 CIFAR-10을 받아둔 경우:

```bash
python scripts/train.py experiment=ddpm_test data.download=false
```

`ddpm_test`는 로컬 환경에서 DDPM 학습/시각화 산출물을 빠르게 점검하기 위한 실험 설정입니다.

## 3) Toy Reproducibility Pipeline (new)

Train:

```bash
python scripts/toy_train.py
```

Fast smoke:

```bash
python scripts/toy_train.py trainer.fast_dev_run=true
```

Sanity checks (initial loss + overfit one batch + fast_dev_run):

```bash
python scripts/toy_sanity_check.py
```

Predict/report:

```bash
python scripts/toy_predict.py
python scripts/toy_report.py
```

## 4) Add New Experiment

Create `configs/experiment/<name>.yaml` with `# @package _global_` and override required fields only.

Run:

```bash
# DDPM base
python scripts/train.py experiment=<name>

# Toy base
python scripts/toy_train.py experiment=<name>
```

## 5) Quality Gates

```bash
ruff check .
black --check .
python -m pytest -q
```

## 6) Durable Memory / Agent Assets

- Working agreements: `AGENTS.md`
- Memory docs: `docs/PROMPT.md`, `docs/PLAN.md`, `docs/IMPLEMENT.md`, `docs/STATUS.md`
- HITL schemas/state machine: `docs/hitl/*`
- HITL context hub: `docs/hitl/ACTIVE.md`
- HITL command interface: `docs/hitl/INTERFACE.md`
- Detailed HITL operation guide: `README_HITL_AUTOMATION.md`
- HITL report channels: `reports/hitl/inbox/`, `reports/hitl/daily.md`, `reports/hitl/weekly.md`
- Repo skills: `.agents/skills/*`
- Automation prompt set (compact 3 + legacy paused 9): `AUTOMATIONS.md`
- Safety config: `.codex/config.toml`, `codex/rules/default.rules`

## 7) Output Locations

- DDPM runs: `outputs/hydra/...`
- Toy runs: `outputs/YYYY-MM-DD/HH-MM-SS/`
- Reports: `reports/`
