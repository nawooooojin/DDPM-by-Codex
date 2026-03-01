from __future__ import annotations

import sys
from pathlib import Path

import hydra
import torch
from omegaconf import DictConfig

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import instantiate_from_cfg, seed_everything


@hydra.main(config_path="../configs", config_name="train_toy", version_base="1.3")
def main(cfg: DictConfig) -> None:
    seed_everything(cfg.seed, deterministic_algorithms=cfg.deterministic_algorithms)

    model = instantiate_from_cfg(cfg.model)
    datamodule = instantiate_from_cfg(cfg.data)

    datamodule.prepare_data()
    datamodule.setup("predict")
    batch = next(iter(datamodule.predict_dataloader()))

    model.eval()
    with torch.no_grad():
        preds = model.predict_step(batch=batch, batch_idx=0)

    out_file = Path("predictions_toy.txt")
    out_file.write_text("\n".join(map(str, preds[:20].tolist())) + "\n", encoding="utf-8")
    print(f"Saved sample predictions to {out_file.resolve()}")


if __name__ == "__main__":
    main()
