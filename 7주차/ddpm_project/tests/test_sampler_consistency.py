"""Tests for DDIM deterministic consistency."""

from __future__ import annotations

import torch
from torch import nn

from src.models.diffusion import GaussianDiffusion
from src.models.samplers import ddim_sample_loop


class ZeroModel(nn.Module):
    """Simple model that predicts zero noise."""

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """Return zero tensor with same shape as input.

        Args:
            x: Noised input.
            t: Timesteps.

        Returns:
            Zero noise prediction.
        """
        del t
        return torch.zeros_like(x)


def test_ddim_eta_zero_is_deterministic_with_same_seed() -> None:
    """DDIM with eta=0 should be deterministic for fixed seed."""
    device = torch.device("cpu")
    diffusion = GaussianDiffusion(
        num_timesteps=100,
        beta_schedule="linear",
        beta_start=1e-4,
        beta_end=2e-2,
        objective="epsilon",
    )
    model = ZeroModel()

    sample1, _ = ddim_sample_loop(
        model=model,
        diffusion=diffusion,
        shape=(4, 3, 32, 32),
        device=device,
        num_steps=20,
        eta=0.0,
        seed=777,
        return_trajectory=False,
    )
    sample2, _ = ddim_sample_loop(
        model=model,
        diffusion=diffusion,
        shape=(4, 3, 32, 32),
        device=device,
        num_steps=20,
        eta=0.0,
        seed=777,
        return_trajectory=False,
    )

    assert torch.allclose(sample1, sample2)
