# HITL State Machine

Canonical states:
- DRAFT
- PLAN_READY
- PLAN_APPROVED
- RUN_READY
- RUN_APPROVED
- RUNNING
- RESULT_READY
- MERGE_APPROVED
- MERGED / REJECTED

Gate rules:
- No code/config mutation before PLAN_APPROVED.
- No run execution before RUN_APPROVED.
- No merge/reflection before MERGE_APPROVED.

Use `state_index.csv` as the minimal registry.
