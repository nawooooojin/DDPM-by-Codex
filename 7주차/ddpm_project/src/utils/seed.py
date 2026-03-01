"""Random seed helpers."""

from __future__ import annotations

import random

import numpy as np
import torch



def set_seed(seed: int) -> None:
    """Set global random seed for DDPM pipeline reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False



def seed_everything(seed: int, deterministic_algorithms: bool = False) -> None:
    """Extended seed helper for Lightning-based toy pipeline."""
    try:
        import lightning as L  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - runtime env dependent
        raise ModuleNotFoundError(
            "lightning is required for seed_everything(). Install project dependencies first."
        ) from exc

    random.seed(seed)
    np.random.seed(seed)
    L.seed_everything(seed, workers=True)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    if deterministic_algorithms:
        torch.use_deterministic_algorithms(True)
