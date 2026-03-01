# HITL Research Automation Workflow

This document describes a reusable Human-in-the-Loop (HITL) automation operating model for research projects.
The goal is to maximize research throughput while keeping critical control with the researcher.

## 1) Why This Workflow

Research velocity is often limited by engineering overhead:
- experiment setup and config wiring
- repetitive run execution
- log parsing and result summarization
- failure triage and reproducibility packaging

This workflow delegates repetitive engineering operations to agents, while preserving researcher control at explicit approval gates.

## 2) Core Principles

- Not fully autonomous research: approvals are mandatory.
- Config-first execution: all hyperparameters and paths in Hydra YAML.
- Reproducibility-first artifacts: every decision leaves durable traces.
- Small, reviewable changes: avoid large opaque edits.
- Safety-first automation: destructive actions require explicit human approval.

## 3) HITL State Machine

Canonical states:
- `DRAFT`
- `PLAN_READY`
- `PLAN_APPROVED`
- `RUN_READY`
- `RUN_APPROVED`
- `RUNNING`
- `RESULT_READY`
- `MERGE_APPROVED`
- `MERGED` or `REJECTED`

Gate policy:
- Before `PLAN_APPROVED`: no code/config mutation.
- Before `RUN_APPROVED`: no training/eval execution.
- Before `MERGE_APPROVED`: no merge to main branch.

Registry file:
- `docs/hitl/state_index.csv`

Required schemas:
- `docs/hitl/experiment_card.yaml`
- `docs/hitl/run_gate.yaml`
- `docs/hitl/result_card.yaml`

## 4) Operating Surface

Project-level durable files:
- [AGENTS.md](/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project/AGENTS.md)
- [docs/PROMPT.md](/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project/docs/PROMPT.md)
- [docs/PLAN.md](/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project/docs/PLAN.md)
- [docs/IMPLEMENT.md](/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project/docs/IMPLEMENT.md)
- [docs/STATUS.md](/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project/docs/STATUS.md)

Reporting channels:
- `reports/hitl/inbox/`
- `reports/hitl/daily.md`
- `reports/hitl/weekly.md`

Global templates:
- Skills: `~/.codex/skills/*`
- Automations: `~/.codex/automations/*/automation.toml`

## 5) Skill Catalog (Recommended)

Essential skills:
- `$bootstrap-hydra-lightning-research`
- `$hitl-experiment-design`
- `$hitl-run-gate`
- `$execute-approved-run`
- `$parse-wandb-lineage`
- `$summarize-batch-results`
- `$qualitative-review-pack`
- `$triage-training-failure`
- `$drift-audit`
- `$repro-bundle`

Mapping by stage:
- Planning: `hitl-experiment-design`, `drift-audit`
- Pre-run gate: `hitl-run-gate`
- Execution: `execute-approved-run`
- Post-run analysis: `parse-wandb-lineage`, `summarize-batch-results`, `qualitative-review-pack`
- Recovery and reliability: `triage-training-failure`, `repro-bundle`

## 6) Automation Templates (Default: PAUSED)

Recommended 9 automations:
- `nightly-health-check`
- `daily-code-delta`
- `daily-hitl-queue-build`
- `run-gate-preflight`
- `run-monitor`
- `failed-run-triage`
- `weekly-experiment-digest`
- `prompt-plan-drift-check`
- `repro-audit`

Default policy:
- Create all as `PAUSED`.
- Activate in phases:
  1. `nightly-health-check`
  2. `prompt-plan-drift-check`
  3. execution-oriented automations after gate discipline is stable

## 7) End-to-End Example (Toy)

### Step A: Draft an experiment card

Use `docs/hitl/experiment_card.yaml`:

```yaml
exp_id: "EXP-TOY-001"
hypothesis: "Lower hidden_dim may reduce overfitting without large accuracy drop."
model_changes:
  - "ToyMLP hidden_dim: 64 -> 32"
config_overrides:
  - "model.hidden_dim=32"
  - "trainer.max_epochs=3"
expected_signal:
  - "Validation loss remains within +5% of baseline."
risk_level: "low"
compute_budget:
  max_wall_time: "00:15:00"
  device: "cpu"
stop_conditions:
  - "Abort if val_loss diverges for 3 consecutive validations."
```

Then write `DRAFT -> PLAN_READY` in `docs/hitl/state_index.csv`.

### Step B: Create run gate card (human approval required)

Use `docs/hitl/run_gate.yaml`:

```yaml
exp_id: "EXP-TOY-001"
exact_command: "python scripts/toy_train.py experiment=ablation_example model.hidden_dim=32 trainer.max_epochs=3"
cwd: "/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project"
max_duration: "00:15:00"
gpu_budget: "0"
artifacts_expected:
  - "outputs/<date>/<time>/checkpoints/*"
  - "outputs/<date>/<time>/.hydra/*"
rollback_plan:
  - "Revert experiment override file if run is rejected."
```

Only after human confirmation: `PLAN_APPROVED -> RUN_READY -> RUN_APPROVED`.

### Step C: Execute approved run

```bash
python scripts/toy_train.py experiment=ablation_example model.hidden_dim=32 trainer.max_epochs=3
```

During execution:
- state transition: `RUN_APPROVED -> RUNNING`

### Step D: Write result card

Use `docs/hitl/result_card.yaml`:

```yaml
exp_id: "EXP-TOY-001"
status: "success"
best_metrics:
  val_loss: 0.72
  val_acc: 0.81
qualitative_notes:
  - "No unstable loss spikes observed."
failure_class: "none"
next_actions:
  - "Compare hidden_dim=16 and hidden_dim=48 for sensitivity."
```

Then state transition:
- `RUNNING -> RESULT_READY -> MERGE_APPROVED -> MERGED` (if human approved)

## 8) Edge/Corner Cases and Policy

Hard failures (must block progress):
- skipping required gate transition
- unknown state labels
- duplicate `exp_id` in state registry
- missing required keys in HITL card schemas
- automation template missing prompt/cwd/status

Soft failures (allow progress with note):
- optional qualitative artifacts not available
- temporary external logging outage (e.g., W&B API timeout)

## 9) Validation Procedure

Primary validation script:

```bash
conda run --no-capture-output -n py311 python scripts/hitl_validate_workflow.py
```

What it validates:
- HITL schema keys
- state registry header/duplicates/unknown states
- global skill existence + quick validation
- automation existence + `PAUSED` + cwd + prompt
- toy state-transition edge/corner cases

Report output:
- `reports/hitl/validation_report_YYYY-MM-DD.md`

## 10) Adoption Checklist for a New Project

1. Bootstrap Hydra + Lightning structure.
2. Install durable docs (`PROMPT/PLAN/IMPLEMENT/STATUS`).
3. Install HITL schemas and state registry under `docs/hitl`.
4. Add report channels under `reports/hitl`.
5. Register skills and paused automations.
6. Run validation script and store report.
7. Activate only health-check and drift-check first.
8. Expand to execution automations after 1-2 stable cycles.

## 11) Practical Notes

- Keep all experiment deltas in `configs/experiment/*.yaml`.
- Never hardcode run-specific paths in source code.
- Prefer explicit `exact_command` in run gate card.
- Keep approval history in markdown logs and commit them.
- Use reproducibility bundles for top-performing runs before merge.

---

If you want to operationalize this pattern in another repository, start by copying:
- `docs/hitl/*`
- `scripts/hitl_validate_workflow.py`
- `AUTOMATIONS.md`
- `AGENTS.md` HITL policy section

