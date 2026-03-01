---
name: "$run-experiment"
description: "configs/experiment에 실험 YAML 생성(오버라이드 포함) + 실행 커맨드 제시 + 출력/로그 경로 표준화"
---

# $run-experiment

1. Create `configs/experiment/<name>.yaml` with `# @package _global_`.
2. Run:
   - DDPM: `python scripts/train.py experiment=<name>`
   - Toy: `python scripts/toy_train.py experiment=<name>`
3. Summarize outputs under `reports/`.
