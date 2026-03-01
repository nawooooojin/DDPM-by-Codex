from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict



def write_text(path: str, content: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")



def render_sanity_markdown(results: Dict[str, Dict[str, object]]) -> str:
    lines = ["# Sanity Check Report", "", f"Generated: {datetime.now().isoformat(timespec='seconds')}", ""]
    lines.append("| Check | Status | Details |")
    lines.append("|---|---|---|")

    for check_name, payload in results.items():
        status = "PASS" if payload.get("passed", False) else "FAIL"
        details = payload.get("details", "")
        lines.append(f"| {check_name} | {status} | {details} |")

    return "\n".join(lines) + "\n"
