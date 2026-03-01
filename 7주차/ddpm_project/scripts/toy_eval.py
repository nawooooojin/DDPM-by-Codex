from __future__ import annotations

import sys
from pathlib import Path

import hydra
from omegaconf import DictConfig

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import instantiate_callbacks, instantiate_from_cfg, seed_everything


@hydra.main(config_path="../configs", config_name="train_toy", version_base="1.3")
def main(cfg: DictConfig) -> None:
    seed_everything(cfg.seed, deterministic_algorithms=cfg.deterministic_algorithms)

    model = instantiate_from_cfg(cfg.model)
    datamodule = instantiate_from_cfg(cfg.data)
    callbacks = instantiate_callbacks(cfg.callbacks)
    trainer = instantiate_from_cfg(cfg.trainer, callbacks=callbacks)

    trainer.validate(model=model, datamodule=datamodule, ckpt_path=cfg.ckpt_path)
    trainer.test(model=model, datamodule=datamodule, ckpt_path=cfg.ckpt_path)


if __name__ == "__main__":
    main()
