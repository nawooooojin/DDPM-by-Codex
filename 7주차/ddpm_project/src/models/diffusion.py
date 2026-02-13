"""Gaussian diffusion process implementation for DDPM training."""

from __future__ import annotations

import math
from typing import Optional, Tuple

import torch
import torch.nn.functional as F
from torch import nn


def _extract(values: torch.Tensor, t: torch.Tensor, shape: torch.Size) -> torch.Tensor:
    """Gather 1D diffusion coefficients for a batch of timesteps.

    Args:
        values: Coefficient tensor with shape [T].
        t: Timestep tensor with shape [B].
        shape: Target tensor shape to broadcast into.

    Returns:
        Broadcastable tensor of shape [B, 1, 1, 1].
    """
    out = values.gather(0, t)
    return out.view(shape[0], 1, 1, 1)


def _cosine_beta_schedule(num_timesteps: int, s: float = 0.008) -> torch.Tensor:
    """Create cosine beta schedule from Improved DDPM.

    Args:
        num_timesteps: Number of diffusion steps.
        s: Small offset used by the schedule.

    Returns:
        Beta tensor with shape [T].
    """
    steps = num_timesteps + 1
    x = torch.linspace(0, num_timesteps, steps, dtype=torch.float64)
    alpha_bars = torch.cos(((x / num_timesteps) + s) / (1 + s) * math.pi * 0.5) ** 2
    alpha_bars = alpha_bars / alpha_bars[0]
    betas = 1 - (alpha_bars[1:] / alpha_bars[:-1])
    return torch.clip(betas, 1e-6, 0.999).float()


class GaussianDiffusion(nn.Module):
    """Core diffusion equations used for DDPM objective."""

    def __init__(
        self,
        num_timesteps: int,
        beta_schedule: str,
        beta_start: float,
        beta_end: float,
        objective: str = "epsilon",
    ) -> None:
        """Initialize diffusion process.

        Args:
            num_timesteps: Number of diffusion timesteps.
            beta_schedule: Beta schedule name. Supports "linear" and "cosine".
            beta_start: Start value for linear schedule.
            beta_end: End value for linear schedule.
            objective: Training objective. Only "epsilon" is supported.

        Raises:
            ValueError: If an unsupported objective or schedule is provided.
        """
        super().__init__()
        if objective != "epsilon":
            raise ValueError("Only epsilon objective is supported in this project.")

        if beta_schedule == "linear":
            betas = torch.linspace(beta_start, beta_end, num_timesteps, dtype=torch.float32)
        elif beta_schedule == "cosine":
            betas = _cosine_beta_schedule(num_timesteps)
        else:
            raise ValueError(f"Unsupported beta schedule: {beta_schedule}")

        alphas = 1.0 - betas
        alpha_bars = torch.cumprod(alphas, dim=0)
        alpha_bars_prev = torch.cat([torch.ones(1), alpha_bars[:-1]], dim=0)

        self.num_timesteps = num_timesteps
        self.objective = objective

        self.register_buffer("betas", betas)
        self.register_buffer("alphas", alphas)
        self.register_buffer("alpha_bars", alpha_bars)
        self.register_buffer("alpha_bars_prev", alpha_bars_prev)

        self.register_buffer("sqrt_alpha_bars", torch.sqrt(alpha_bars))
        self.register_buffer("sqrt_one_minus_alpha_bars", torch.sqrt(1.0 - alpha_bars))
        self.register_buffer("sqrt_recip_alphas", torch.sqrt(1.0 / alphas))

        posterior_variance = betas * (1.0 - alpha_bars_prev) / (1.0 - alpha_bars)
        posterior_variance[0] = 1e-20
        self.register_buffer("posterior_variance", posterior_variance)
        self.register_buffer("posterior_log_variance", torch.log(torch.clamp(posterior_variance, min=1e-20)))

        posterior_mean_coef1 = betas * torch.sqrt(alpha_bars_prev) / (1.0 - alpha_bars)
        posterior_mean_coef2 = (1.0 - alpha_bars_prev) * torch.sqrt(alphas) / (1.0 - alpha_bars)
        self.register_buffer("posterior_mean_coef1", posterior_mean_coef1)
        self.register_buffer("posterior_mean_coef2", posterior_mean_coef2)

    def sample_timesteps(self, batch_size: int, device: torch.device) -> torch.Tensor:
        """Sample timesteps uniformly.

        Args:
            batch_size: Batch size.
            device: Target device.

        Returns:
            Sampled timesteps [B].
        """
        return torch.randint(0, self.num_timesteps, (batch_size,), device=device, dtype=torch.long)

    def q_sample(self, x0: torch.Tensor, t: torch.Tensor, noise: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Diffuse clean image x0 to xt at timestep t.

        Args:
            x0: Clean image tensor [B, C, H, W].
            t: Timestep tensor [B].
            noise: Optional pre-sampled Gaussian noise [B, C, H, W].

        Returns:
            Noised image xt with same shape as x0.
        """
        if noise is None:
            noise = torch.randn_like(x0)
        mean = _extract(self.sqrt_alpha_bars, t, x0.shape) * x0
        std = _extract(self.sqrt_one_minus_alpha_bars, t, x0.shape)
        return mean + std * noise

    def predict_x0_from_eps(self, x_t: torch.Tensor, t: torch.Tensor, eps: torch.Tensor) -> torch.Tensor:
        """Recover x0 prediction from epsilon prediction.

        Args:
            x_t: Noised image [B, C, H, W].
            t: Timestep tensor [B].
            eps: Predicted noise [B, C, H, W].

        Returns:
            Predicted clean image x0.
        """
        sqrt_alpha_bar = _extract(self.sqrt_alpha_bars, t, x_t.shape)
        sqrt_one_minus_alpha_bar = _extract(self.sqrt_one_minus_alpha_bars, t, x_t.shape)
        return (x_t - sqrt_one_minus_alpha_bar * eps) / sqrt_alpha_bar

    def q_posterior(self, x0: torch.Tensor, x_t: torch.Tensor, t: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute q(x_{t-1} | x_t, x0).

        Args:
            x0: Clean image estimate [B, C, H, W].
            x_t: Current noised image [B, C, H, W].
            t: Timestep tensor [B].

        Returns:
            Tuple of posterior mean and variance tensors.
        """
        mean = _extract(self.posterior_mean_coef1, t, x_t.shape) * x0 + _extract(
            self.posterior_mean_coef2, t, x_t.shape
        ) * x_t
        variance = _extract(self.posterior_variance, t, x_t.shape)
        return mean, variance

    def p_mean_variance(self, model: nn.Module, x_t: torch.Tensor, t: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute model posterior parameters p_theta(x_{t-1} | x_t).

        Args:
            model: Noise prediction model.
            x_t: Current noised image [B, C, H, W].
            t: Timestep tensor [B].

        Returns:
            Tuple of mean and variance tensors.
        """
        eps_pred = model(x_t, t)
        x0_pred = self.predict_x0_from_eps(x_t, t, eps_pred).clamp(-1.0, 1.0)
        mean, variance = self.q_posterior(x0_pred, x_t, t)
        return mean, variance

    def training_losses(self, model: nn.Module, x0: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """Compute DDPM training loss for epsilon objective.

        Args:
            model: Noise prediction model.
            x0: Clean image batch [B, C, H, W].
            t: Timestep batch [B].

        Returns:
            Scalar MSE loss tensor.
        """
        noise = torch.randn_like(x0)
        x_t = self.q_sample(x0, t, noise)
        eps_pred = model(x_t, t)
        return F.mse_loss(eps_pred, noise)
