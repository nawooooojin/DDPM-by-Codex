"""Visualization utilities for DDPM study outputs."""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, Tuple

import matplotlib.pyplot as plt
import torch
from torchvision.utils import make_grid

from src.models.diffusion import GaussianDiffusion


def _to_display_tensor(images: torch.Tensor) -> torch.Tensor:
    """Convert [-1, 1] images to [0, 1] for visualization.

    Args:
        images: Input tensor.

    Returns:
        Converted tensor.
    """
    return images.detach().cpu().clamp(-1.0, 1.0).add(1.0).mul(0.5)


def _save_grid(images: torch.Tensor, path: Path, nrow: int = 8) -> None:
    """Save image grid to file.

    Args:
        images: Image tensor [B, C, H, W] in [-1, 1].
        path: Output path.
        nrow: Number of images per row.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    grid = make_grid(_to_display_tensor(images), nrow=nrow)
    plt.figure(figsize=(8, 8))
    plt.axis("off")
    plt.imshow(grid.permute(1, 2, 0).numpy())
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def save_noise_schedule_curves(diffusion: GaussianDiffusion, path: Path) -> None:
    """Save beta, alpha_bar, and SNR curves.

    Args:
        diffusion: Diffusion instance.
        path: Output path.
    """
    betas = diffusion.betas.detach().cpu().numpy()
    alpha_bars = diffusion.alpha_bars.detach().cpu().numpy()
    snr = alpha_bars / (1.0 - alpha_bars + 1e-8)

    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 3, 1)
    plt.plot(betas)
    plt.title("Beta")
    plt.subplot(1, 3, 2)
    plt.plot(alpha_bars)
    plt.title("Alpha Bar")
    plt.subplot(1, 3, 3)
    plt.plot(snr)
    plt.title("SNR")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def save_forward_noising_grid(
    diffusion: GaussianDiffusion,
    images: torch.Tensor,
    timesteps: Sequence[int],
    path: Path,
) -> None:
    """Save forward noising progression for a batch.

    Args:
        diffusion: Diffusion instance.
        images: Clean image batch [B, C, H, W].
        timesteps: Timesteps to visualize.
        path: Output path.
    """
    batch = images[: min(images.size(0), 8)]
    valid_timesteps = [max(0, min(int(t), diffusion.num_timesteps - 1)) for t in timesteps]

    rows: List[torch.Tensor] = []
    for t_val in valid_timesteps:
        t = torch.full((batch.size(0),), t_val, device=batch.device, dtype=torch.long)
        rows.append(diffusion.q_sample(batch, t))

    n_rows = len(rows)
    n_cols = batch.size(0)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 1.4, n_rows * 1.6), squeeze=False)

    for row_idx, (t_val, row_images) in enumerate(zip(valid_timesteps, rows)):
        row_disp = _to_display_tensor(row_images)
        for col_idx in range(n_cols):
            axes[row_idx, col_idx].imshow(row_disp[col_idx].permute(1, 2, 0).numpy())
            axes[row_idx, col_idx].axis("off")
            if row_idx == 0:
                axes[row_idx, col_idx].set_title(f"img {col_idx + 1}", fontsize=8)
        axes[row_idx, 0].set_ylabel(f"t={t_val}", fontsize=8, rotation=0, labelpad=16, va="center")

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.suptitle("Forward Noising Progression", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def save_reverse_trajectory_grid(frames: List[Tuple[int, torch.Tensor]], path: Path) -> None:
    """Save sampled reverse trajectory frames.

    Args:
        frames: List of tuples (timestep, sample batch tensor).
        path: Output path.
    """
    if not frames:
        return

    n_rows = len(frames)
    n_cols = min(frames[0][1].size(0), 8)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 1.4, n_rows * 1.6), squeeze=False)

    for row_idx, (t_val, frame) in enumerate(frames):
        frame_disp = _to_display_tensor(frame[:n_cols])
        for col_idx in range(n_cols):
            axes[row_idx, col_idx].imshow(frame_disp[col_idx].permute(1, 2, 0).numpy())
            axes[row_idx, col_idx].axis("off")
            if row_idx == 0:
                axes[row_idx, col_idx].set_title(f"img {col_idx + 1}", fontsize=8)
        axes[row_idx, 0].set_ylabel(f"t={t_val}", fontsize=8, rotation=0, labelpad=16, va="center")

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.suptitle("Reverse Denoising Trajectory", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def save_loss_curve(losses: List[float], path: Path) -> None:
    """Save training loss curve.

    Args:
        losses: Sequence of loss values.
        path: Output path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4))
    plt.plot(losses)
    plt.xlabel("Step")
    plt.ylabel("Loss")
    plt.title("Training Loss")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def save_sample_comparison(ddpm_samples: torch.Tensor, ddim_samples: torch.Tensor, path: Path) -> None:
    """Save side-by-side DDPM and DDIM sample grids.

    Args:
        ddpm_samples: DDPM samples [B, C, H, W].
        ddim_samples: DDIM samples [B, C, H, W].
        path: Output path.
    """
    count = min(ddpm_samples.size(0), ddim_samples.size(0), 32)
    ddpm = ddpm_samples[:count]
    ddim = ddim_samples[:count]

    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 6))

    grid_ddpm = make_grid(_to_display_tensor(ddpm), nrow=8)
    grid_ddim = make_grid(_to_display_tensor(ddim), nrow=8)

    plt.subplot(2, 1, 1)
    plt.title("DDPM Samples")
    plt.axis("off")
    plt.imshow(grid_ddpm.permute(1, 2, 0).numpy())

    plt.subplot(2, 1, 2)
    plt.title("DDIM Samples")
    plt.axis("off")
    plt.imshow(grid_ddim.permute(1, 2, 0).numpy())

    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
