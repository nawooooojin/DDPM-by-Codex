from __future__ import annotations

import math
import sys
from pathlib import Path

import hydra
import torch
import torch.nn.functional as F
from omegaconf import DictConfig, OmegaConf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import (
    instantiate_from_cfg,
    render_sanity_markdown,
    seed_everything,
    write_text,
)



def _clone_cfg(cfg: DictConfig) -> DictConfig:
    return OmegaConf.create(OmegaConf.to_container(cfg, resolve=False))



def run_initial_loss_check(cfg: DictConfig) -> dict:
    model = instantiate_from_cfg(cfg.model)
    datamodule = instantiate_from_cfg(cfg.data)

    datamodule.prepare_data()
    datamodule.setup("fit")
    x, y = next(iter(datamodule.train_dataloader()))

    model.eval()
    with torch.no_grad():
        logits = model(x)
        initial_loss = float(F.cross_entropy(logits, y).item())

    theoretical_loss = float(-math.log(1.0 / float(cfg.data.num_classes)))
    delta = abs(initial_loss - theoretical_loss)
    passed = delta <= float(cfg.sanity.initial_loss_tolerance)

    return {
        "passed": passed,
        "details": (
            f"initial_loss={initial_loss:.4f}, theoretical={theoretical_loss:.4f}, "
            f"abs_delta={delta:.4f}, tolerance={cfg.sanity.initial_loss_tolerance}"
        ),
    }



def run_overfit_one_batch_check(cfg: DictConfig) -> dict:
    overfit_cfg = _clone_cfg(cfg)
    overfit_cfg.trainer.fast_dev_run = False
    overfit_cfg.trainer.max_epochs = int(cfg.sanity.overfit.max_epochs)
    overfit_cfg.trainer.overfit_batches = 1.0
    overfit_cfg.trainer.limit_val_batches = 0
    overfit_cfg.trainer.limit_test_batches = 0
    overfit_cfg.trainer.enable_checkpointing = False
    overfit_cfg.trainer.logger = False

    model = instantiate_from_cfg(overfit_cfg.model)
    datamodule = instantiate_from_cfg(overfit_cfg.data)
    trainer = instantiate_from_cfg(overfit_cfg.trainer, callbacks=[])

    trainer.fit(model, datamodule=datamodule)

    final_train_loss = model.latest_train_loss
    target = float(cfg.sanity.overfit.target_train_loss)
    passed = final_train_loss is not None and final_train_loss <= target

    return {
        "passed": passed,
        "details": (
            f"final_train_loss={final_train_loss}, target<={target}, "
            f"max_epochs={cfg.sanity.overfit.max_epochs}"
        ),
    }



def run_fast_dev_run_check(cfg: DictConfig) -> dict:
    smoke_cfg = _clone_cfg(cfg)
    smoke_cfg.trainer.fast_dev_run = True
    smoke_cfg.trainer.enable_checkpointing = False
    smoke_cfg.trainer.logger = False

    model = instantiate_from_cfg(smoke_cfg.model)
    datamodule = instantiate_from_cfg(smoke_cfg.data)
    trainer = instantiate_from_cfg(smoke_cfg.trainer, callbacks=[])

    trainer.fit(model, datamodule=datamodule)
    trainer.test(model=model, datamodule=datamodule)

    return {"passed": True, "details": "trainer.fast_dev_run=True completed for fit+test"}


@hydra.main(config_path="../configs", config_name="train_toy", version_base="1.3")
def main(cfg: DictConfig) -> None:
    seed_everything(cfg.seed, deterministic_algorithms=cfg.deterministic_algorithms)
    results = {}

    try:
        results["initial_loss_sanity"] = run_initial_loss_check(cfg)
    except Exception as exc:
        results["initial_loss_sanity"] = {"passed": False, "details": f"error={exc}"}

    try:
        results["overfit_one_batch"] = run_overfit_one_batch_check(cfg)
    except Exception as exc:
        results["overfit_one_batch"] = {"passed": False, "details": f"error={exc}"}

    try:
        results["fast_dev_run"] = run_fast_dev_run_check(cfg)
    except Exception as exc:
        results["fast_dev_run"] = {"passed": False, "details": f"error={exc}"}

    markdown = render_sanity_markdown(results)
    write_text(cfg.sanity.output_report_path, markdown)
    print(markdown)


if __name__ == "__main__":
    main()
