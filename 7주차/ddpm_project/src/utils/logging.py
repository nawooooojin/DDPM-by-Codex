"""Logging and experiment metadata utilities."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import torch
from omegaconf import DictConfig, OmegaConf

try:
    import wandb
except Exception:
    wandb = None


def get_git_commit_hash(repo_dir: Optional[Path] = None) -> str:
    """Return current git commit hash.

    Returns:
        Short git hash if available, else "unknown".
    """
    cmd = ["git"]
    if repo_dir is not None:
        cmd.extend(["-C", str(repo_dir)])
    cmd.extend(["rev-parse", "--short", "HEAD"])
    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
        return output
    except Exception:
        return "unknown"


def dump_run_metadata(cfg: DictConfig, output_dir: Path, repo_dir: Optional[Path] = None) -> None:
    """Persist config and run metadata.

    Args:
        cfg: Hydra config.
        output_dir: Run output directory.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    OmegaConf.save(cfg, output_dir / "resolved_config.yaml")
    metadata = {
        "git_commit": get_git_commit_hash(repo_dir=repo_dir),
        "seed": cfg.seed,
    }
    (output_dir / "run_metadata.txt").write_text(
        "\n".join(f"{k}: {v}" for k, v in metadata.items()),
        encoding="utf-8",
    )


def init_wandb(cfg: DictConfig, run_dir: Path) -> Any:
    """Initialize Weights & Biases run when enabled.

    Args:
        cfg: Hydra config.
        run_dir: Current run directory.

    Returns:
        WandB run object or None.
    """
    if not cfg.logging.use_wandb or wandb is None:
        return None

    run = wandb.init(
        project=cfg.logging.project,
        entity=cfg.logging.entity,
        mode=cfg.logging.mode,
        name=cfg.logging.run_name_template,
        config=OmegaConf.to_container(cfg, resolve=True),
        dir=str(run_dir),
    )
    return run


def log_metrics(run: Any, metrics: Dict[str, float], step: int) -> None:
    """Log scalar metrics.

    Args:
        run: WandB run object.
        metrics: Metric dictionary.
        step: Global step.
    """
    if run is None:
        return
    run.log(metrics, step=step)


def _to_image_array(image: torch.Tensor) -> np.ndarray:
    """Convert normalized tensor image to uint8 array.

    Args:
        image: Tensor image [C, H, W] in [-1, 1].

    Returns:
        NumPy image [H, W, C] in uint8.
    """
    image = image.detach().cpu().clamp(-1.0, 1.0)
    image = (image + 1.0) * 0.5
    image = image.permute(1, 2, 0).numpy()
    return (image * 255.0).astype(np.uint8)


def log_image_grid(run: Any, key: str, images: torch.Tensor, step: int, max_items: int = 16) -> None:
    """Log image list to WandB.

    Args:
        run: WandB run object.
        key: Log key.
        images: Tensor batch [B, C, H, W] in [-1, 1].
        step: Global step.
        max_items: Maximum number of images to log.
    """
    if run is None or wandb is None:
        return

    previews = [_to_image_array(img) for img in images[:max_items]]
    run.log({key: [wandb.Image(img) for img in previews]}, step=step)


def finish_wandb(run: Any) -> None:
    """Finish WandB run.

    Args:
        run: WandB run object.
    """
    if run is not None:
        run.finish()
