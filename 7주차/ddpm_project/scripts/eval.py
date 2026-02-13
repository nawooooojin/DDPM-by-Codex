"""Evaluate checkpoint and generate DDPM/DDIM comparison visuals."""

from __future__ import annotations

from pathlib import Path
import sys

import hydra
import torch
from hydra.core.hydra_config import HydraConfig
from hydra.utils import get_original_cwd, instantiate
from omegaconf import DictConfig
from torch import nn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.diffusion import GaussianDiffusion
from src.models.samplers import ddim_sample_loop, ddpm_sample_loop
from src.utils.checkpoint import load_checkpoint
from src.utils.ema import ModelEMA
from src.utils.logging import finish_wandb, init_wandb, log_image_grid
from src.utils.seed import set_seed
from src.utils.viz import save_reverse_trajectory_grid, save_sample_comparison


def _resolve_device(device_cfg: str) -> torch.device:
    """Resolve runtime device from config.

    Args:
        device_cfg: Device string.

    Returns:
        Resolved torch device.
    """
    if device_cfg != "auto":
        return torch.device(device_cfg)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@hydra.main(version_base=None, config_path="../configs", config_name="train")
def main(cfg: DictConfig) -> None:
    """Run evaluation and sampling comparison.

    Args:
        cfg: Hydra configuration object.

    Raises:
        ValueError: If checkpoint path is not provided.
    """
    set_seed(int(cfg.seed))
    device = _resolve_device(str(cfg.runtime.device))

    if cfg.runtime.checkpoint_path is None:
        raise ValueError("runtime.checkpoint_path must be provided for eval.")

    original_cwd = Path(get_original_cwd())
    checkpoint_path = Path(str(cfg.runtime.checkpoint_path))
    if not checkpoint_path.is_absolute():
        checkpoint_path = original_cwd / checkpoint_path

    run_dir = Path(HydraConfig.get().runtime.output_dir)
    figures_dir = run_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    model: nn.Module = instantiate(cfg.model).to(device)
    diffusion: GaussianDiffusion = instantiate(cfg.diffusion).to(device)
    ema = ModelEMA(model, float(cfg.runtime.ema_decay)) if bool(cfg.runtime.ema) else None

    step = load_checkpoint(checkpoint_path, model, optimizer=None, ema=ema, map_location=str(device))

    if ema is not None:
        ema.store(model)
        ema.copy_to(model)

    wandb_run = init_wandb(cfg, run_dir)

    ddpm_samples, ddpm_frames = ddpm_sample_loop(
        model=model,
        diffusion=diffusion,
        shape=(int(cfg.runtime.num_eval_samples), int(cfg.model.in_channels), int(cfg.model.image_size), int(cfg.model.image_size)),
        device=device,
        num_steps=int(cfg.diffusion.num_timesteps),
        seed=int(cfg.runtime.eval_seed),
        return_trajectory=True,
        trajectory_frames=int(cfg.sampler.trajectory_frames),
    )

    ddim_samples, ddim_frames = ddim_sample_loop(
        model=model,
        diffusion=diffusion,
        shape=(int(cfg.runtime.num_eval_samples), int(cfg.model.in_channels), int(cfg.model.image_size), int(cfg.model.image_size)),
        device=device,
        num_steps=50,
        eta=0.0,
        seed=int(cfg.runtime.eval_seed),
        return_trajectory=True,
        trajectory_frames=int(cfg.sampler.trajectory_frames),
    )

    save_reverse_trajectory_grid(ddpm_frames, figures_dir / "reverse_trajectory_ddpm.png")
    save_reverse_trajectory_grid(ddim_frames, figures_dir / "reverse_trajectory_ddim.png")
    save_sample_comparison(ddpm_samples, ddim_samples, figures_dir / "ddpm_vs_ddim_samples.png")

    log_image_grid(wandb_run, "eval/ddpm_samples", ddpm_samples, step=step)
    log_image_grid(wandb_run, "eval/ddim_samples", ddim_samples, step=step)

    finish_wandb(wandb_run)

    if ema is not None:
        ema.restore(model)

    print(f"Evaluation complete. Artifacts saved to: {run_dir}")


if __name__ == "__main__":
    main()
