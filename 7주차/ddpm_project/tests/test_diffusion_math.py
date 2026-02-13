"""Tests for diffusion forward process math boundaries."""

from __future__ import annotations

import torch

from src.models.diffusion import GaussianDiffusion


def test_q_sample_matches_closed_form_for_zero_noise() -> None:
    """q_sample should match sqrt(alpha_bar_t) * x0 when noise is zero."""
    diffusion = GaussianDiffusion(
        num_timesteps=1000,
        beta_schedule="linear",
        beta_start=1e-4,
        beta_end=2e-2,
        objective="epsilon",
    )

    x0 = torch.randn(2, 3, 32, 32)
    noise = torch.zeros_like(x0)

    t0 = torch.zeros(2, dtype=torch.long)
    xt0 = diffusion.q_sample(x0, t0, noise=noise)
    expected0 = diffusion.sqrt_alpha_bars[0] * x0
    assert torch.allclose(xt0, expected0, atol=1e-5)

    t_last = torch.full((2,), diffusion.num_timesteps - 1, dtype=torch.long)
    xt_last = diffusion.q_sample(x0, t_last, noise=noise)
    expected_last = diffusion.sqrt_alpha_bars[-1] * x0
    assert torch.allclose(xt_last, expected_last, atol=1e-5)
