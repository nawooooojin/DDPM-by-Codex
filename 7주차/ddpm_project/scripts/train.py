"""Train DDPM model with pure PyTorch, Hydra, and WandB."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Iterator, Tuple

import hydra
import torch
from hydra.core.hydra_config import HydraConfig
from hydra.utils import get_original_cwd, instantiate
from omegaconf import DictConfig, OmegaConf
from torch import nn
from torch.nn.utils import clip_grad_norm_
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.diffusion import GaussianDiffusion
from src.models.samplers import ddim_sample_loop, ddpm_sample_loop
from src.utils.checkpoint import load_checkpoint, save_checkpoint
from src.utils.ema import ModelEMA
from src.utils.logging import dump_run_metadata, finish_wandb, init_wandb, log_image_grid, log_metrics
from src.utils.seed import set_seed
from src.utils.viz import (
    save_forward_noising_grid,
    save_loss_curve,
    save_noise_schedule_curves,
    save_reverse_trajectory_grid,
    save_sample_comparison,
)


def _resolve_device(device_cfg: str) -> torch.device:
    """Resolve runtime device from config.

    Args:
        device_cfg: Device string from config.

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


def _cycle(loader: DataLoader) -> Iterator[Tuple[torch.Tensor, torch.Tensor]]:
    """Yield dataloader batches indefinitely.

    Args:
        loader: Input dataloader.

    Yields:
        Batch tuple.
    """
    while True:
        for batch in loader:
            yield batch


def _build_optimizer(cfg: DictConfig, model: nn.Module) -> torch.optim.Optimizer:
    """Build optimizer from config.

    Args:
        cfg: Optimizer config.
        model: Trainable model.

    Returns:
        Torch optimizer.

    Raises:
        ValueError: If optimizer name is unsupported.
    """
    if cfg.name.lower() == "adam":
        return torch.optim.Adam(
            model.parameters(),
            lr=float(cfg.lr),
            betas=(float(cfg.betas[0]), float(cfg.betas[1])),
            weight_decay=float(cfg.weight_decay),
        )
    raise ValueError(f"Unsupported optimizer: {cfg.name}")


def _sample_from_config(
    model: nn.Module,
    diffusion: GaussianDiffusion,
    sampler_cfg: DictConfig,
    shape: Tuple[int, ...],
    device: torch.device,
    seed: int,
    return_trajectory: bool,
) -> Tuple[torch.Tensor, list[tuple[int, torch.Tensor]]]:
    """Sample images with configured sampler.

    Args:
        model: Trained model.
        diffusion: Diffusion process.
        sampler_cfg: Sampler config block.
        shape: Requested output tensor shape.
        device: Sampling device.
        seed: Random seed for reproducibility.
        return_trajectory: Whether to include intermediate frames.

    Returns:
        Final sample tensor and trajectory list.

    Raises:
        ValueError: If sampler name is unsupported.
    """
    sampler_name = str(sampler_cfg.name).lower()
    if sampler_name == "ddpm":
        return ddpm_sample_loop(
            model=model,
            diffusion=diffusion,
            shape=shape,
            device=device,
            num_steps=int(sampler_cfg.num_sampling_steps),
            eta=float(sampler_cfg.eta),
            seed=seed,
            return_trajectory=return_trajectory,
            trajectory_frames=int(sampler_cfg.trajectory_frames),
        )
    if sampler_name == "ddim":
        return ddim_sample_loop(
            model=model,
            diffusion=diffusion,
            shape=shape,
            device=device,
            num_steps=int(sampler_cfg.num_sampling_steps),
            eta=float(sampler_cfg.eta),
            seed=seed,
            return_trajectory=return_trajectory,
            trajectory_frames=int(sampler_cfg.trajectory_frames),
        )
    raise ValueError(f"Unsupported sampler: {sampler_cfg.name}")


def _apply_ema_if_enabled(model: nn.Module, ema: ModelEMA | None) -> None:
    """Temporarily copy EMA parameters into model.

    Args:
        model: Model for evaluation.
        ema: Optional EMA tracker.
    """
    if ema is not None:
        ema.store(model)
        ema.copy_to(model)


def _restore_ema_if_enabled(model: nn.Module, ema: ModelEMA | None) -> None:
    """Restore non-EMA parameters after evaluation.

    Args:
        model: Model for training.
        ema: Optional EMA tracker.
    """
    if ema is not None:
        ema.restore(model)


@hydra.main(version_base=None, config_path="../configs", config_name="train")
def main(cfg: DictConfig) -> None:
    """Train DDPM with custom PyTorch loop.

    Args:
        cfg: Hydra configuration object.
    """
    set_seed(int(cfg.seed))
    device = _resolve_device(str(cfg.runtime.device))

    run_dir = Path(HydraConfig.get().runtime.output_dir)
    original_cwd = Path(get_original_cwd())
    dump_run_metadata(cfg, run_dir, repo_dir=original_cwd)

    data_root = Path(str(cfg.data.root))
    if not data_root.is_absolute():
        data_root = original_cwd / data_root

    train_loader, val_loader = instantiate(
        cfg.data,
        root=str(data_root),
        overfit_one_batch=bool(cfg.runtime.overfit_one_batch),
    )

    model: nn.Module = instantiate(cfg.model).to(device)
    diffusion: GaussianDiffusion = instantiate(cfg.diffusion).to(device)
    optimizer = _build_optimizer(cfg.optimizer, model)

    ema = ModelEMA(model, float(cfg.runtime.ema_decay)) if bool(cfg.runtime.ema) else None

    global_step = 0
    if cfg.runtime.resume_from is not None:
        resume_path = Path(str(cfg.runtime.resume_from))
        if not resume_path.is_absolute():
            resume_path = original_cwd / resume_path
        global_step = load_checkpoint(resume_path, model, optimizer=optimizer, ema=ema, map_location=str(device))

    wandb_run = init_wandb(cfg, run_dir)

    total_steps = int(cfg.runtime.total_steps)
    if bool(cfg.runtime.fast_dev_run):
        total_steps = min(total_steps, 10)

    checkpoints_dir = run_dir / "checkpoints"
    figures_dir = run_dir / "figures"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    train_iterator = _cycle(train_loader)
    running_losses: list[float] = []

    for step in range(global_step + 1, total_steps + 1):
        model.train()
        images, _ = next(train_iterator)
        images = images.to(device)

        timesteps = diffusion.sample_timesteps(images.size(0), device)
        loss = diffusion.training_losses(model, images, timesteps)

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        if float(cfg.runtime.grad_clip_norm) > 0:
            clip_grad_norm_(model.parameters(), max_norm=float(cfg.runtime.grad_clip_norm))
        optimizer.step()

        if ema is not None:
            ema.update(model)

        loss_value = float(loss.item())
        running_losses.append(loss_value)

        if step == 1:
            print(f"[Sanity] Initial theoretical-loss check at step=1: loss={loss_value:.6f}")

        if step % int(cfg.logging.log_every) == 0 or step == total_steps:
            log_metrics(wandb_run, {"train/loss": loss_value}, step=step)
            print(f"[Train] step={step} loss={loss_value:.6f}")

        if step % int(cfg.runtime.sample_every) == 0 or step == total_steps:
            _apply_ema_if_enabled(model, ema)
            sampled, _ = _sample_from_config(
                model=model,
                diffusion=diffusion,
                sampler_cfg=cfg.sampler,
                shape=(int(cfg.runtime.num_eval_samples), int(cfg.model.in_channels), int(cfg.model.image_size), int(cfg.model.image_size)),
                device=device,
                seed=int(cfg.runtime.eval_seed),
                return_trajectory=False,
            )
            _restore_ema_if_enabled(model, ema)
            if bool(cfg.logging.log_images):
                sampler_key = str(cfg.sampler.name).lower()
                log_image_grid(wandb_run, f"samples/{sampler_key}", sampled, step=step)

        if step % int(cfg.runtime.save_every) == 0 or step == total_steps:
            save_checkpoint(
                path=checkpoints_dir / f"step_{step}.pt",
                step=step,
                model=model,
                optimizer=optimizer,
                ema=ema,
                config=OmegaConf.to_container(cfg, resolve=True),
            )
            save_checkpoint(
                path=checkpoints_dir / "last.pt",
                step=step,
                model=model,
                optimizer=optimizer,
                ema=ema,
                config=OmegaConf.to_container(cfg, resolve=True),
            )

    model.eval()
    preview_images, _ = next(iter(val_loader))
    preview_images = preview_images.to(device)

    _apply_ema_if_enabled(model, ema)

    save_noise_schedule_curves(diffusion, figures_dir / "noise_schedule_curves.png")
    forward_timesteps = (
        torch.linspace(0, diffusion.num_timesteps - 1, steps=6).round().long().tolist()
    )

    save_forward_noising_grid(
        diffusion=diffusion,
        images=preview_images,
        timesteps=forward_timesteps,
        path=figures_dir / "forward_noising_grid.png",
    )

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

    _restore_ema_if_enabled(model, ema)

    save_reverse_trajectory_grid(ddpm_frames, figures_dir / "reverse_trajectory_ddpm.png")
    save_reverse_trajectory_grid(ddim_frames, figures_dir / "reverse_trajectory_ddim.png")
    save_sample_comparison(ddpm_samples, ddim_samples, figures_dir / "ddpm_vs_ddim_samples.png")
    save_loss_curve(running_losses, figures_dir / "train_loss_curve.png")

    if running_losses:
        first_loss = running_losses[0]
        last_loss = running_losses[-1]
        print(f"[Sanity] Loss trend first={first_loss:.6f} last={last_loss:.6f}")

    finish_wandb(wandb_run)
    print(f"Training complete. Artifacts saved to: {run_dir}")


if __name__ == "__main__":
    main()
