# HITL Workflow Validation Report

- Generated at: `2026-03-01T16:43:35`
- Python: `3.11.14`
- Total checks: `78`
- Passed: `78`
- Failed: `0`

## Check Results

| Check | Status | Details |
|---|---|---|
| experiment_card_schema | PASS | keys_ok=['compute_budget', 'config_overrides', 'exp_id', 'expected_signal', 'hypothesis', 'lane', 'model_changes', 'promotion_reason', 'promotion_source', 'risk_level', 'stop_conditions'] |
| run_gate_schema | PASS | keys_ok=['artifacts_expected', 'cwd', 'exact_command', 'exp_id', 'gpu_budget', 'max_duration', 'rollback_plan'] |
| result_card_schema | PASS | keys_ok=['best_metrics', 'exp_id', 'failure_class', 'next_actions', 'qualitative_notes', 'status'] |
| state_registry_valid | PASS | rows=0 |
| active_hub_sections | PASS | sections_ok |
| interface_commands_present | PASS | sections_ok |
| skill_bootstrap-hydra-lightning-research_files_exist | PASS | path=/Users/woojinna/.codex/skills/bootstrap-hydra-lightning-research |
| skill_bootstrap-hydra-lightning-research_quick_validate | PASS | Skill is valid! |
| skill_hitl-experiment-design_files_exist | PASS | path=/Users/woojinna/.codex/skills/hitl-experiment-design |
| skill_hitl-experiment-design_quick_validate | PASS | Skill is valid! |
| skill_hitl-run-gate_files_exist | PASS | path=/Users/woojinna/.codex/skills/hitl-run-gate |
| skill_hitl-run-gate_quick_validate | PASS | Skill is valid! |
| skill_execute-approved-run_files_exist | PASS | path=/Users/woojinna/.codex/skills/execute-approved-run |
| skill_execute-approved-run_quick_validate | PASS | Skill is valid! |
| skill_parse-wandb-lineage_files_exist | PASS | path=/Users/woojinna/.codex/skills/parse-wandb-lineage |
| skill_parse-wandb-lineage_quick_validate | PASS | Skill is valid! |
| skill_summarize-batch-results_files_exist | PASS | path=/Users/woojinna/.codex/skills/summarize-batch-results |
| skill_summarize-batch-results_quick_validate | PASS | Skill is valid! |
| skill_qualitative-review-pack_files_exist | PASS | path=/Users/woojinna/.codex/skills/qualitative-review-pack |
| skill_qualitative-review-pack_quick_validate | PASS | Skill is valid! |
| skill_triage-training-failure_files_exist | PASS | path=/Users/woojinna/.codex/skills/triage-training-failure |
| skill_triage-training-failure_quick_validate | PASS | Skill is valid! |
| skill_drift-audit_files_exist | PASS | path=/Users/woojinna/.codex/skills/drift-audit |
| skill_drift-audit_quick_validate | PASS | Skill is valid! |
| skill_repro-bundle_files_exist | PASS | path=/Users/woojinna/.codex/skills/repro-bundle |
| skill_repro-bundle_quick_validate | PASS | Skill is valid! |
| compact_automation_daily-hitl-digest_paused | PASS | status=PAUSED |
| compact_automation_daily-hitl-digest_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| compact_automation_daily-hitl-digest_prompt_nonempty | PASS | prompt_set |
| compact_automation_run-on-approval_paused | PASS | status=PAUSED |
| compact_automation_run-on-approval_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| compact_automation_run-on-approval_prompt_nonempty | PASS | prompt_set |
| compact_automation_weekly-research-review_paused | PASS | status=PAUSED |
| compact_automation_weekly-research-review_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| compact_automation_weekly-research-review_prompt_nonempty | PASS | prompt_set |
| legacy_automation_nightly-health-check_paused | PASS | status=PAUSED |
| legacy_automation_nightly-health-check_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| legacy_automation_nightly-health-check_prompt_nonempty | PASS | prompt_set |
| legacy_automation_daily-code-delta_paused | PASS | status=PAUSED |
| legacy_automation_daily-code-delta_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| legacy_automation_daily-code-delta_prompt_nonempty | PASS | prompt_set |
| legacy_automation_daily-hitl-queue-build_paused | PASS | status=PAUSED |
| legacy_automation_daily-hitl-queue-build_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| legacy_automation_daily-hitl-queue-build_prompt_nonempty | PASS | prompt_set |
| legacy_automation_run-gate-preflight_paused | PASS | status=PAUSED |
| legacy_automation_run-gate-preflight_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| legacy_automation_run-gate-preflight_prompt_nonempty | PASS | prompt_set |
| legacy_automation_run-monitor_paused | PASS | status=PAUSED |
| legacy_automation_run-monitor_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| legacy_automation_run-monitor_prompt_nonempty | PASS | prompt_set |
| legacy_automation_failed-run-triage_paused | PASS | status=PAUSED |
| legacy_automation_failed-run-triage_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| legacy_automation_failed-run-triage_prompt_nonempty | PASS | prompt_set |
| legacy_automation_weekly-experiment-digest_paused | PASS | status=PAUSED |
| legacy_automation_weekly-experiment-digest_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| legacy_automation_weekly-experiment-digest_prompt_nonempty | PASS | prompt_set |
| legacy_automation_prompt-plan-drift-check_paused | PASS | status=PAUSED |
| legacy_automation_prompt-plan-drift-check_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| legacy_automation_prompt-plan-drift-check_prompt_nonempty | PASS | prompt_set |
| legacy_automation_repro-audit_paused | PASS | status=PAUSED |
| legacy_automation_repro-audit_cwd_exists | PASS | cwds=['/Users/woojinna/001_Personal_Learning/001_26 겨울 CGV 비전&생성모델 스터디/7주차/ddpm_project'] |
| legacy_automation_repro-audit_prompt_nonempty | PASS | prompt_set |
| case_happy_path | PASS | expected=True, actual=True, detail=ok |
| case_skip_plan_approval | PASS | expected=False, actual=False, detail=blocked_transition=PLAN_READY->RUN_READY |
| case_skip_run_approval | PASS | expected=False, actual=False, detail=blocked_transition=RUN_READY->RUNNING |
| case_unknown_state | PASS | expected=False, actual=False, detail=unknown_state=RUN_PLANET |
| case_terminal_escape | PASS | expected=False, actual=False, detail=blocked_transition=REJECTED->PLAN_READY |
| case_start_from_run_ready | PASS | expected=False, actual=False, detail=invalid_start=RUN_READY |
| lane_baseline_record | PASS | expected=record, actual=record |
| lane_gpu_budget_record | PASS | expected=record, actual=record |
| lane_cpu_budget_record | PASS | expected=record, actual=record |
| lane_external_share_record | PASS | expected=record, actual=record |
| lane_fast_wip | PASS | expected=wip, actual=wip |
| run_block_record_without_approval | PASS | record lane should block execution before RUN_APPROVED |
| run_allow_wip_without_approval | PASS | wip lane allows fast execution without approval |
| merge_requires_merge_approved | PASS | merge requires MERGE_APPROVED |
| corner_duplicate_exp_id_detected | PASS | duplicates=['EXP-1'] |
| corner_missing_yaml_keys_detected | PASS | missing=['compute_budget', 'config_overrides', 'expected_signal', 'lane', 'promotion_reason', 'promotion_source', 'risk_level', 'stop_conditions'] |

## Summary
- Validation succeeded. Compact HITL templates and controls are consistent.
