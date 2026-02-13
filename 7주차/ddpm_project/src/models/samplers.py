"""Sampling loops for DDPM and DDIM."""

from __future__ import annotations

from typing import List, Optional, Tuple

import torch
from torch import nn

from src.models.diffusion import GaussianDiffusion


def _make_generator(device: torch.device, seed: Optional[int]) -> Optional[torch.Generator]:
    """Create a deterministic random generator when a seed is provided.

    Args:
        device: Target device.
        seed: Optional random seed.

    Returns:
        Torch generator or None.
    """
    if seed is None:
        return None
    generator = torch.Generator(device=device)
    generator.manual_seed(seed)
    return generator


def _capture_frame(step_idx: int, total_steps: int, max_frames: int) -> bool:
    """Decide whether to keep a trajectory frame.

    Args:
        step_idx: Current loop index.
        total_steps: Total number of sampling steps.
        max_frames: Maximum number of captured frames.

    Returns:
        True if this step should be captured.
    """
    if max_frames <= 0:
        return False
    stride = max(total_steps // max_frames, 1)
    return step_idx % stride == 0 or step_idx == total_steps - 1


def ddpm_sample_loop(
    model: nn.Module,
    diffusion: GaussianDiffusion,
    shape: Tuple[int, ...],
    device: torch.device,
    num_steps: Optional[int] = None,
    eta: float = 0.0,
    seed: Optional[int] = None,
    return_trajectory: bool = False,
    trajectory_frames: int = 10,
) -> Tuple[torch.Tensor, List[Tuple[int, torch.Tensor]]]:
    """Run ancestral DDPM sampling loop.

    Args:
        model: Trained noise prediction model.
        diffusion: Diffusion process instance.
        shape: Output tensor shape, e.g., (B, 3, 32, 32).
        device: Sampling device.
        num_steps: Number of reverse steps. Defaults to full timeline.
        eta: Unused parameter included for a shared interface.
        seed: Optional random seed.
        return_trajectory: Whether to return intermediate samples.
        trajectory_frames: Maximum number of trajectory frames to keep.

    Returns:
        Final sampled tensor and optional trajectory frame list.
    """
    del eta
    model.eval()
    generator = _make_generator(device, seed)

    total_steps = diffusion.num_timesteps if num_steps is None else num_steps
    if total_steps <= 0:
        raise ValueError("num_steps must be positive")

    if total_steps == diffusion.num_timesteps:
        timeline = list(range(diffusion.num_timesteps - 1, -1, -1))
    else:
        indices = torch.linspace(0, diffusion.num_timesteps - 1, total_steps)
        timeline = [int(i.item()) for i in torch.round(indices).flip(0)]

    x_t = torch.randn(shape, device=device, generator=generator)
    trajectory: List[Tuple[int, torch.Tensor]] = []

    with torch.no_grad():
        for step_idx, t_val in enumerate(timeline):
            t = torch.full((shape[0],), t_val, device=device, dtype=torch.long)
            mean, variance = diffusion.p_mean_variance(model, x_t, t)
            if t_val > 0:
                noise = torch.randn(shape, device=device, generator=generator)
            else:
                noise = torch.zeros_like(x_t)
            x_t = mean + torch.sqrt(variance) * noise

            if return_trajectory and _capture_frame(step_idx, len(timeline), trajectory_frames):
                trajectory.append((t_val, x_t.detach().cpu()))

    return x_t, trajectory


def ddim_sample_loop(
    model: nn.Module,
    diffusion: GaussianDiffusion,
    shape: Tuple[int, ...],
    device: torch.device,
    num_steps: Optional[int] = None,
    eta: float = 0.0,
    seed: Optional[int] = None,
    return_trajectory: bool = False,
    trajectory_frames: int = 10,
) -> Tuple[torch.Tensor, List[Tuple[int, torch.Tensor]]]:
    """Run DDIM sampling loop.

    Args:
        model: Trained noise prediction model.
        diffusion: Diffusion process instance.
        shape: Output tensor shape, e.g., (B, 3, 32, 32).
        device: Sampling device.
        num_steps: Number of DDIM steps.
        eta: DDIM stochasticity factor.
        seed: Optional random seed.
        return_trajectory: Whether to return intermediate samples.
        trajectory_frames: Maximum number of trajectory frames to keep.

    Returns:
        Final sampled tensor and optional trajectory frame list.
    """
    model.eval()
    generator = _make_generator(device, seed)

    steps = diffusion.num_timesteps if num_steps is None else num_steps
    if steps <= 0:
        raise ValueError("num_steps must be positive")

    step_indices = torch.linspace(0, diffusion.num_timesteps - 1, steps)
    step_indices = torch.round(step_indices).long().to(device)

    x_t = torch.randn(shape, device=device, generator=generator)
    trajectory: List[Tuple[int, torch.Tensor]] = []

    with torch.no_grad():
        for step_idx in range(steps - 1, -1, -1):
            t_val = int(step_indices[step_idx].item())
            t = torch.full((shape[0],), t_val, device=device, dtype=torch.long)

            eps = model(x_t, t)
            alpha_bar_t = diffusion.alpha_bars[t_val]

            if step_idx > 0:
                prev_t_val = int(step_indices[step_idx - 1].item())
                alpha_bar_prev = diffusion.alpha_bars[prev_t_val]
            else:
                alpha_bar_prev = torch.tensor(1.0, device=device)

            sqrt_alpha_bar_t = torch.sqrt(alpha_bar_t)
            sqrt_one_minus_alpha_bar_t = torch.sqrt(1.0 - alpha_bar_t)
            x0_pred = (x_t - sqrt_one_minus_alpha_bar_t * eps) / sqrt_alpha_bar_t
            x0_pred = x0_pred.clamp(-1.0, 1.0)

            sigma = (
                eta
                * torch.sqrt((1.0 - alpha_bar_prev) / (1.0 - alpha_bar_t))
                * torch.sqrt(1.0 - alpha_bar_t / alpha_bar_prev)
            )
            directional = torch.sqrt(torch.clamp(1.0 - alpha_bar_prev - sigma**2, min=0.0)) * eps

            if step_idx > 0:
                noise = torch.randn(shape, device=device, generator=generator)
            else:
                noise = torch.zeros_like(x_t)

            x_t = torch.sqrt(alpha_bar_prev) * x0_pred + directional + sigma * noise

            if return_trajectory and _capture_frame(steps - 1 - step_idx, steps, trajectory_frames):
                trajectory.append((t_val, x_t.detach().cpu()))

    return x_t, trajectory
