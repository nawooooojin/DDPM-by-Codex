"""Validate HITL workflow contracts, compact automation policy, and edge cases.

Run from project root:
    conda run --no-capture-output -n py311 python scripts/hitl_validate_workflow.py
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Sequence, Tuple

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("Python 3.11+ is required (tomllib missing).") from exc


HITL_STATES: Sequence[str] = (
    "DRAFT",
    "PLAN_READY",
    "PLAN_APPROVED",
    "RUN_READY",
    "RUN_APPROVED",
    "RUNNING",
    "RESULT_READY",
    "MERGE_APPROVED",
    "MERGED",
    "REJECTED",
)

ALLOWED_TRANSITIONS: Dict[str, set[str]] = {
    "DRAFT": {"PLAN_READY", "REJECTED"},
    "PLAN_READY": {"PLAN_APPROVED", "REJECTED"},
    "PLAN_APPROVED": {"RUN_READY", "REJECTED"},
    "RUN_READY": {"RUN_APPROVED", "REJECTED"},
    "RUN_APPROVED": {"RUNNING", "REJECTED"},
    "RUNNING": {"RESULT_READY", "REJECTED"},
    "RESULT_READY": {"MERGE_APPROVED", "REJECTED"},
    "MERGE_APPROVED": {"MERGED", "REJECTED"},
    "MERGED": set(),
    "REJECTED": set(),
}

ALLOWED_LANES: set[str] = {"wip", "record"}

REQUIRED_EXPERIMENT_KEYS: set[str] = {
    "exp_id",
    "lane",
    "promotion_source",
    "promotion_reason",
    "hypothesis",
    "model_changes",
    "config_overrides",
    "expected_signal",
    "risk_level",
    "compute_budget",
    "stop_conditions",
}
REQUIRED_RUN_GATE_KEYS: set[str] = {
    "exp_id",
    "exact_command",
    "cwd",
    "max_duration",
    "gpu_budget",
    "artifacts_expected",
    "rollback_plan",
}
REQUIRED_RESULT_KEYS: set[str] = {
    "exp_id",
    "status",
    "best_metrics",
    "qualitative_notes",
    "failure_class",
    "next_actions",
}
REQUIRED_STATE_COLUMNS: Sequence[str] = (
    "exp_id",
    "state",
    "owner",
    "updated_at",
    "approved_by",
    "lane",
    "needs_human_action",
    "next_gate",
)

COMPACT_AUTOMATIONS: Sequence[str] = (
    "daily-hitl-digest",
    "run-on-approval",
    "weekly-research-review",
)

LEGACY_AUTOMATIONS: Sequence[str] = (
    "nightly-health-check",
    "daily-code-delta",
    "daily-hitl-queue-build",
    "run-gate-preflight",
    "run-monitor",
    "failed-run-triage",
    "weekly-experiment-digest",
    "prompt-plan-drift-check",
    "repro-audit",
)

EXPECTED_SKILLS: Sequence[str] = (
    "bootstrap-hydra-lightning-research",
    "hitl-experiment-design",
    "hitl-run-gate",
    "execute-approved-run",
    "parse-wandb-lineage",
    "summarize-batch-results",
    "qualitative-review-pack",
    "triage-training-failure",
    "drift-audit",
    "repro-bundle",
)

REQUIRED_ACTIVE_SECTIONS: Sequence[str] = (
    "# ACTIVE HITL Context Hub",
    "## Active Experiments",
    "## Current Gate Focus",
    "## Next Human Actions",
    "## Latest Failure (1 item)",
    "## Today Top 3",
)

REQUIRED_INTERFACE_PHRASES: Sequence[str] = (
    "실험 제안:",
    "계획 승인:",
    "실행 승인:",
    "결과 정리:",
    "머지 승인:",
)


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str


def top_level_yaml_keys(path: Path) -> set[str]:
    """Extract top-level YAML keys with a conservative parser."""

    key_pattern = re.compile(r"^([A-Za-z0-9_]+):")
    keys: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith(" "):
            continue
        match = key_pattern.match(line)
        if match:
            keys.add(match.group(1))
    return keys


def validate_required_yaml_keys(path: Path, required: set[str], name: str) -> CheckResult:
    keys = top_level_yaml_keys(path)
    missing = sorted(required - keys)
    return CheckResult(
        name=name,
        passed=not missing,
        details=f"missing={missing}" if missing else f"keys_ok={sorted(keys)}",
    )


def validate_state_registry(path: Path) -> CheckResult:
    if not path.exists():
        return CheckResult("state_registry_exists", False, f"missing_file={path}")

    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        header = reader.fieldnames or []
        if tuple(header) != tuple(REQUIRED_STATE_COLUMNS):
            return CheckResult("state_registry_header", False, f"header={header}")
        for row in reader:
            rows.append(row)

    exp_ids: list[str] = [row["exp_id"] for row in rows if row["exp_id"]]
    duplicates = sorted({exp_id for exp_id in exp_ids if exp_ids.count(exp_id) > 1})
    unknown_states = sorted({row["state"] for row in rows if row["state"] and row["state"] not in HITL_STATES})
    unknown_lanes = sorted({row["lane"] for row in rows if row["lane"] and row["lane"] not in ALLOWED_LANES})

    if duplicates:
        return CheckResult("state_registry_duplicate_exp_id", False, f"duplicates={duplicates}")
    if unknown_states:
        return CheckResult("state_registry_unknown_state", False, f"unknown_states={unknown_states}")
    if unknown_lanes:
        return CheckResult("state_registry_unknown_lane", False, f"unknown_lanes={unknown_lanes}")
    return CheckResult("state_registry_valid", True, f"rows={len(rows)}")


def validate_text_sections(path: Path, required_markers: Sequence[str], name: str) -> CheckResult:
    if not path.exists():
        return CheckResult(name, False, f"missing_file={path}")
    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in required_markers if marker not in text]
    return CheckResult(name, not missing, f"missing={missing}" if missing else "sections_ok")


def validate_transition_sequence(states: Sequence[str]) -> Tuple[bool, str]:
    if not states:
        return False, "empty_sequence"
    if states[0] not in ("DRAFT", "PLAN_READY"):
        return False, f"invalid_start={states[0]}"
    for state in states:
        if state not in HITL_STATES:
            return False, f"unknown_state={state}"
    for current_state, next_state in zip(states, states[1:]):
        allowed = ALLOWED_TRANSITIONS[current_state]
        if next_state not in allowed:
            return False, f"blocked_transition={current_state}->{next_state}"
    return True, "ok"


def classify_lane(
    baseline_included: bool,
    estimated_gpu_hours: float,
    estimated_cpu_hours: float,
    external_share_target: bool,
) -> str:
    if baseline_included:
        return "record"
    if estimated_gpu_hours >= 1.0:
        return "record"
    if estimated_cpu_hours >= 4.0:
        return "record"
    if external_share_target:
        return "record"
    return "wip"


def can_execute_run(lane: str, state: str) -> bool:
    if lane == "wip":
        return True
    return state in {"RUN_APPROVED", "RUNNING"}


def can_merge(state: str) -> bool:
    return state in {"MERGE_APPROVED", "MERGED"}


def run_toy_state_cases() -> list[CheckResult]:
    cases = [
        (
            "case_happy_path",
            ["DRAFT", "PLAN_READY", "PLAN_APPROVED", "RUN_READY", "RUN_APPROVED", "RUNNING", "RESULT_READY", "MERGE_APPROVED", "MERGED"],
            True,
        ),
        ("case_skip_plan_approval", ["DRAFT", "PLAN_READY", "RUN_READY"], False),
        ("case_skip_run_approval", ["DRAFT", "PLAN_READY", "PLAN_APPROVED", "RUN_READY", "RUNNING"], False),
        ("case_unknown_state", ["DRAFT", "PLAN_READY", "RUN_PLANET"], False),
        ("case_terminal_escape", ["DRAFT", "PLAN_READY", "REJECTED", "PLAN_READY"], False),
        ("case_start_from_run_ready", ["RUN_READY", "RUN_APPROVED"], False),
    ]
    results: list[CheckResult] = []
    for name, sequence, expected in cases:
        passed, detail = validate_transition_sequence(sequence)
        results.append(CheckResult(name, passed == expected, f"expected={expected}, actual={passed}, detail={detail}"))
    return results


def run_lane_policy_cases() -> list[CheckResult]:
    results: list[CheckResult] = []
    classify_cases = [
        ("lane_baseline_record", (True, 0.0, 0.1, False), "record"),
        ("lane_gpu_budget_record", (False, 1.0, 0.0, False), "record"),
        ("lane_cpu_budget_record", (False, 0.0, 4.0, False), "record"),
        ("lane_external_share_record", (False, 0.0, 0.0, True), "record"),
        ("lane_fast_wip", (False, 0.2, 1.5, False), "wip"),
    ]
    for name, args, expected in classify_cases:
        actual = classify_lane(*args)
        results.append(CheckResult(name, actual == expected, f"expected={expected}, actual={actual}"))

    results.append(
        CheckResult(
            "run_block_record_without_approval",
            can_execute_run("record", "PLAN_APPROVED") is False,
            "record lane should block execution before RUN_APPROVED",
        )
    )
    results.append(
        CheckResult(
            "run_allow_wip_without_approval",
            can_execute_run("wip", "DRAFT") is True,
            "wip lane allows fast execution without approval",
        )
    )
    results.append(
        CheckResult(
            "merge_requires_merge_approved",
            can_merge("RUNNING") is False and can_merge("MERGE_APPROVED") is True,
            "merge requires MERGE_APPROVED",
        )
    )
    return results


def run_toy_corner_cases() -> list[CheckResult]:
    results: list[CheckResult] = []
    with tempfile.TemporaryDirectory(prefix="hitl_validation_") as tmpdir:
        tmp = Path(tmpdir)

        dup_state_file = tmp / "state_index_dup.csv"
        dup_state_file.write_text(
            "exp_id,state,owner,updated_at,approved_by,lane,needs_human_action,next_gate\n"
            "EXP-1,DRAFT,alice,2026-03-01T10:00:00,alice,record,yes,PLAN_APPROVED\n"
            "EXP-1,PLAN_READY,alice,2026-03-01T10:05:00,alice,record,yes,PLAN_APPROVED\n",
            encoding="utf-8",
        )
        dup_result = validate_state_registry(dup_state_file)
        results.append(
            CheckResult(
                "corner_duplicate_exp_id_detected",
                (not dup_result.passed and "duplicates=" in dup_result.details),
                dup_result.details,
            )
        )

        invalid_yaml = tmp / "experiment_card_bad.yaml"
        invalid_yaml.write_text(
            "exp_id: \"EXP-TEST\"\n"
            "hypothesis: \"x\"\n"
            "model_changes:\n"
            "  - \"none\"\n",
            encoding="utf-8",
        )
        bad_yaml_result = validate_required_yaml_keys(
            invalid_yaml, REQUIRED_EXPERIMENT_KEYS, "corner_missing_yaml_keys"
        )
        results.append(
            CheckResult(
                "corner_missing_yaml_keys_detected",
                not bad_yaml_result.passed and "missing=" in bad_yaml_result.details,
                bad_yaml_result.details,
            )
        )
    return results


def validate_automations(automations_root: Path, automation_ids: Sequence[str], prefix: str) -> list[CheckResult]:
    results: list[CheckResult] = []

    for automation_id in automation_ids:
        file_path = automations_root / automation_id / "automation.toml"
        if not file_path.exists():
            results.append(CheckResult(f"{prefix}_{automation_id}_exists", False, "missing_automation.toml"))
            continue

        data = tomllib.loads(file_path.read_text(encoding="utf-8"))
        status_ok = data.get("status") == "PAUSED"
        results.append(CheckResult(f"{prefix}_{automation_id}_paused", status_ok, f"status={data.get('status')}"))

        cwd_list = data.get("cwds", [])
        cwd_ok = bool(cwd_list) and all(Path(path).exists() for path in cwd_list)
        results.append(CheckResult(f"{prefix}_{automation_id}_cwd_exists", cwd_ok, f"cwds={cwd_list}"))

        prompt_ok = bool(str(data.get("prompt", "")).strip())
        results.append(
            CheckResult(
                f"{prefix}_{automation_id}_prompt_nonempty",
                prompt_ok,
                "prompt_set" if prompt_ok else "prompt_empty",
            )
        )

    return results


def validate_global_skills(skills_root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    quick_validate_script = skills_root / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    for skill in EXPECTED_SKILLS:
        skill_dir = skills_root / skill
        exists = (skill_dir / "SKILL.md").exists() and (skill_dir / "agents" / "openai.yaml").exists()
        results.append(CheckResult(f"skill_{skill}_files_exist", exists, f"path={skill_dir}"))
        if not exists:
            continue

        proc = subprocess.run(
            [sys.executable, str(quick_validate_script), str(skill_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        results.append(
            CheckResult(
                f"skill_{skill}_quick_validate",
                proc.returncode == 0,
                proc.stdout.strip() if proc.returncode == 0 else proc.stderr.strip(),
            )
        )
    return results


def render_report(results: Sequence[CheckResult], report_path: Path) -> None:
    timestamp = dt.datetime.now().isoformat(timespec="seconds")
    passed = [result for result in results if result.passed]
    failed = [result for result in results if not result.passed]

    lines = [
        "# HITL Workflow Validation Report",
        "",
        f"- Generated at: `{timestamp}`",
        f"- Python: `{sys.version.split()[0]}`",
        f"- Total checks: `{len(results)}`",
        f"- Passed: `{len(passed)}`",
        f"- Failed: `{len(failed)}`",
        "",
        "## Check Results",
        "",
        "| Check | Status | Details |",
        "|---|---|---|",
    ]

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"| {result.name} | {status} | {result.details} |")

    lines.append("")
    lines.append("## Summary")
    if failed:
        lines.append("- Validation failed. Review failed checks above.")
    else:
        lines.append("- Validation succeeded. Compact HITL templates and controls are consistent.")
    lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate HITL workflow contracts, automations, and edge cases.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Path to project root (default: current working directory).",
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=Path.home() / ".codex" / "skills",
        help="Path to global skills root.",
    )
    parser.add_argument(
        "--automations-root",
        type=Path,
        default=Path.home() / ".codex" / "automations",
        help="Path to global automations root.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=None,
        help="Optional report output path (default: reports/hitl/validation_report_YYYYMMDD.md).",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    today = dt.date.today().isoformat()
    report_path = args.report_path or (project_root / "reports" / "hitl" / f"validation_report_{today}.md")

    docs_hitl = project_root / "docs" / "hitl"
    checks: list[CheckResult] = []

    checks.append(
        validate_required_yaml_keys(
            docs_hitl / "experiment_card.yaml",
            REQUIRED_EXPERIMENT_KEYS,
            "experiment_card_schema",
        )
    )
    checks.append(
        validate_required_yaml_keys(
            docs_hitl / "run_gate.yaml",
            REQUIRED_RUN_GATE_KEYS,
            "run_gate_schema",
        )
    )
    checks.append(
        validate_required_yaml_keys(
            docs_hitl / "result_card.yaml",
            REQUIRED_RESULT_KEYS,
            "result_card_schema",
        )
    )
    checks.append(validate_state_registry(docs_hitl / "state_index.csv"))
    checks.append(
        validate_text_sections(
            docs_hitl / "ACTIVE.md",
            REQUIRED_ACTIVE_SECTIONS,
            "active_hub_sections",
        )
    )
    checks.append(
        validate_text_sections(
            docs_hitl / "INTERFACE.md",
            REQUIRED_INTERFACE_PHRASES,
            "interface_commands_present",
        )
    )

    checks.extend(validate_global_skills(args.skills_root.resolve()))
    checks.extend(validate_automations(args.automations_root.resolve(), COMPACT_AUTOMATIONS, "compact_automation"))
    checks.extend(validate_automations(args.automations_root.resolve(), LEGACY_AUTOMATIONS, "legacy_automation"))
    checks.extend(run_toy_state_cases())
    checks.extend(run_lane_policy_cases())
    checks.extend(run_toy_corner_cases())

    render_report(checks, report_path)
    failed_count = len([check for check in checks if not check.passed])

    print(f"Validation report written: {report_path}")
    print(f"Total checks={len(checks)}, failed={failed_count}")
    return 1 if failed_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
