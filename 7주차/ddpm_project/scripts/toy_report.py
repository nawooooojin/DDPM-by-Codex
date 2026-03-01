from __future__ import annotations

import sys
from pathlib import Path

import hydra
from omegaconf import DictConfig

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import write_text



def _collect_latest_runs(outputs_dir: Path, n_latest: int) -> list[Path]:
    if not outputs_dir.exists():
        return []
    runs = [p for p in outputs_dir.glob("*/*") if p.is_dir()]
    runs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return runs[:n_latest]


@hydra.main(config_path="../configs", config_name="train_toy", version_base="1.3")
def main(cfg: DictConfig) -> None:
    runs = _collect_latest_runs(Path("outputs"), int(cfg.report.n_latest))

    lines = ["# Latest Experiment Summary", "", "| Run Directory | Modified |", "|---|---|"]
    for run_dir in runs:
        lines.append(f"| `{run_dir}` | {run_dir.stat().st_mtime:.0f} |")

    if not runs:
        lines.append("| (none) | - |")

    content = "\n".join(lines) + "\n"
    write_text(cfg.report.output_path, content)
    print(content)


if __name__ == "__main__":
    main()
