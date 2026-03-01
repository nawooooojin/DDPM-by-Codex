---
name: "$add-model"
description: "src/models에 새 모델 추가 + configs/model에 YAML 추가 + tests에 shape 테스트 추가"
---

# $add-model

1. Add model at `src/models/<name>.py`.
2. Add `_target_` config in `configs/model/<name>.yaml`.
3. Register export (if safe) in package init.
4. Add shape tests under `tests/`.
