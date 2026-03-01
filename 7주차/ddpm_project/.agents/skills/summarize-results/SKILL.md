---
name: "$summarize-results"
description: "outputs/ 또는 W&B(가능하면)를 읽어 최근 N개 실험을 표로 요약하고 reports/latest.md 갱신"
---

# $summarize-results

Use:
- `python scripts/toy_report.py report.n_latest=10 report.output_path=reports/latest.md`

If W&B enabled, include run IDs and artifact linkage.
