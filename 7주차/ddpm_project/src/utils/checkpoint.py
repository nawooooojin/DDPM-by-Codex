"""Checkpoint save/load utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import torch
from torch import nn

from src.utils.ema import ModelEMA


def save_checkpoint(
    path: Path,
    step: int,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    ema: Optional[ModelEMA],
    config: Dict[str, Any],
) -> None:
    """Save model training checkpoint.

    Args:
        path: Destination file path.
        step: Global step.
        model: Model instance.
        optimizer: Optimizer instance.
        ema: Optional EMA tracker.
        config: Serialized run config.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "step": step,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "config": config,
    }
    if ema is not None:
        payload["ema"] = ema.state_dict()

    torch.save(payload, path)


def load_checkpoint(
    path: Path,
    model: nn.Module,
    optimizer: Optional[torch.optim.Optimizer] = None,
    ema: Optional[ModelEMA] = None,
    map_location: str = "cpu",
) -> int:
    """Load checkpoint and restore states.

    Args:
        path: Checkpoint path.
        model: Model to restore.
        optimizer: Optional optimizer to restore.
        ema: Optional EMA tracker to restore.
        map_location: torch.load map location.

    Returns:
        Restored global step.
    """
    payload = torch.load(path, map_location=map_location)
    model.load_state_dict(payload["model"])

    if optimizer is not None and "optimizer" in payload:
        optimizer.load_state_dict(payload["optimizer"])

    if ema is not None and "ema" in payload:
        ema.load_state_dict(payload["ema"])

    return int(payload.get("step", 0))
