"""U-Net backbone for DDPM epsilon prediction."""

from __future__ import annotations

import math
from typing import List

import torch
from torch import nn


def _group_norm(num_channels: int) -> nn.GroupNorm:
    """Create a valid GroupNorm layer for a channel size.

    Args:
        num_channels: Number of channels in the input tensor.

    Returns:
        GroupNorm layer with a divisor-compatible number of groups.
    """
    groups = min(32, num_channels)
    while groups > 1 and num_channels % groups != 0:
        groups -= 1
    return nn.GroupNorm(groups, num_channels)


class SinusoidalTimeEmbedding(nn.Module):
    """Sinusoidal embedding for diffusion timesteps."""

    def __init__(self, dim: int) -> None:
        """Initialize embedding module.

        Args:
            dim: Embedding dimension.
        """
        super().__init__()
        self.dim = dim

    def forward(self, t: torch.Tensor) -> torch.Tensor:
        """Embed timestep indices into sinusoidal vectors.

        Args:
            t: Timestep indices with shape [B].

        Returns:
            Embedded timesteps with shape [B, dim].
        """
        half_dim = self.dim // 2
        device = t.device
        exponent = -math.log(10000.0) / max(half_dim - 1, 1)
        frequencies = torch.exp(torch.arange(half_dim, device=device) * exponent)
        angles = t.float().unsqueeze(1) * frequencies.unsqueeze(0)
        embedding = torch.cat([torch.sin(angles), torch.cos(angles)], dim=1)
        if self.dim % 2 == 1:
            embedding = torch.cat([embedding, torch.zeros_like(embedding[:, :1])], dim=1)
        return embedding


class ResBlock(nn.Module):
    """Residual block conditioned on timestep embedding."""

    def __init__(self, in_channels: int, out_channels: int, time_dim: int, dropout: float) -> None:
        """Initialize residual block.

        Args:
            in_channels: Number of input channels.
            out_channels: Number of output channels.
            time_dim: Time embedding dimension.
            dropout: Dropout probability.
        """
        super().__init__()
        self.norm1 = _group_norm(in_channels)
        self.act1 = nn.SiLU()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)

        self.time_proj = nn.Sequential(
            nn.SiLU(),
            nn.Linear(time_dim, out_channels),
        )

        self.norm2 = _group_norm(out_channels)
        self.act2 = nn.SiLU()
        self.dropout = nn.Dropout(dropout)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)

        if in_channels != out_channels:
            self.skip = nn.Conv2d(in_channels, out_channels, kernel_size=1)
        else:
            self.skip = nn.Identity()

    def forward(self, x: torch.Tensor, t_emb: torch.Tensor) -> torch.Tensor:
        """Apply residual transformation.

        Args:
            x: Feature map of shape [B, C, H, W].
            t_emb: Time embedding of shape [B, time_dim].

        Returns:
            Transformed feature map with shape [B, out_channels, H, W].
        """
        h = self.conv1(self.act1(self.norm1(x)))
        time_term = self.time_proj(t_emb).unsqueeze(-1).unsqueeze(-1)
        h = h + time_term
        h = self.conv2(self.dropout(self.act2(self.norm2(h))))
        return h + self.skip(x)


class SelfAttention2d(nn.Module):
    """Self-attention block for 2D feature maps."""

    def __init__(self, channels: int, num_heads: int = 4) -> None:
        """Initialize attention block.

        Args:
            channels: Input and output channel size.
            num_heads: Number of attention heads.
        """
        super().__init__()
        self.channels = channels
        self.num_heads = max(1, min(num_heads, channels))
        while channels % self.num_heads != 0 and self.num_heads > 1:
            self.num_heads -= 1

        self.norm = _group_norm(channels)
        self.qkv = nn.Conv2d(channels, channels * 3, kernel_size=1)
        self.proj = nn.Conv2d(channels, channels, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply self-attention.

        Args:
            x: Feature map of shape [B, C, H, W].

        Returns:
            Attention-enhanced feature map of shape [B, C, H, W].
        """
        b, c, h, w = x.shape
        qkv = self.qkv(self.norm(x))
        q, k, v = torch.chunk(qkv, 3, dim=1)

        head_dim = c // self.num_heads
        q = q.reshape(b, self.num_heads, head_dim, h * w)
        k = k.reshape(b, self.num_heads, head_dim, h * w)
        v = v.reshape(b, self.num_heads, head_dim, h * w)

        attn = torch.einsum("bnci,bncj->bnij", q, k) * (head_dim**-0.5)
        attn = torch.softmax(attn, dim=-1)
        out = torch.einsum("bnij,bncj->bnci", attn, v)
        out = out.reshape(b, c, h, w)
        out = self.proj(out)
        return x + out


class UNet(nn.Module):
    """Time-conditioned U-Net for diffusion noise prediction."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        base_channels: int,
        channel_mult: List[int],
        num_res_blocks: int,
        attn_resolutions: List[int],
        dropout: float,
        image_size: int,
    ) -> None:
        """Initialize U-Net.

        Args:
            in_channels: Number of input channels.
            out_channels: Number of output channels.
            base_channels: Base channel width.
            channel_mult: Channel multiplier per level.
            num_res_blocks: Number of residual blocks per level.
            attn_resolutions: Spatial resolutions where attention is enabled.
            dropout: Dropout probability.
            image_size: Input image size.
        """
        super().__init__()
        time_dim = base_channels * 4

        self.time_embed = nn.Sequential(
            SinusoidalTimeEmbedding(base_channels),
            nn.Linear(base_channels, time_dim),
            nn.SiLU(),
            nn.Linear(time_dim, time_dim),
        )

        self.input_conv = nn.Conv2d(in_channels, base_channels, kernel_size=3, padding=1)

        self.down_stages = nn.ModuleList()
        self.downsamples = nn.ModuleList()
        self.skip_channels: List[int] = []

        ch = base_channels
        resolution = image_size
        levels = len(channel_mult)

        for level, mult in enumerate(channel_mult):
            stage = nn.ModuleList()
            out_ch = base_channels * mult
            for _ in range(num_res_blocks):
                block = ResBlock(ch, out_ch, time_dim, dropout)
                attention: nn.Module
                if resolution in attn_resolutions:
                    attention = SelfAttention2d(out_ch)
                else:
                    attention = nn.Identity()
                stage.append(nn.ModuleList([block, attention]))
                ch = out_ch
                self.skip_channels.append(ch)

            self.down_stages.append(stage)

            if level != levels - 1:
                self.downsamples.append(nn.Conv2d(ch, ch, kernel_size=3, stride=2, padding=1))
                resolution //= 2
                self.skip_channels.append(ch)
            else:
                self.downsamples.append(nn.Identity())

        self.mid_block1 = ResBlock(ch, ch, time_dim, dropout)
        self.mid_attn = SelfAttention2d(ch)
        self.mid_block2 = ResBlock(ch, ch, time_dim, dropout)

        self.up_stages = nn.ModuleList()
        self.upsamples = nn.ModuleList()

        skip_channels_stack = list(self.skip_channels)
        resolution = image_size // (2 ** (levels - 1))

        for level in reversed(range(levels)):
            stage = nn.ModuleList()
            out_ch = base_channels * channel_mult[level]
            # Each non-top level also consumes one downsample skip from encoder.
            blocks_in_level = num_res_blocks + (1 if level != 0 else 0)

            for _ in range(blocks_in_level):
                skip_ch = skip_channels_stack.pop()
                block = ResBlock(ch + skip_ch, out_ch, time_dim, dropout)
                attention = SelfAttention2d(out_ch) if resolution in attn_resolutions else nn.Identity()
                stage.append(nn.ModuleList([block, attention]))
                ch = out_ch

            self.up_stages.append(stage)
            if level != 0:
                self.upsamples.append(nn.ConvTranspose2d(ch, ch, kernel_size=4, stride=2, padding=1))
                resolution *= 2

        self.output_norm = _group_norm(ch)
        self.output_act = nn.SiLU()
        self.output_conv = nn.Conv2d(ch, out_channels, kernel_size=3, padding=1)

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """Predict noise from noised image and timestep.

        Args:
            x: Input tensor of shape [B, 3, 32, 32].
            t: Timestep tensor of shape [B].

        Returns:
            Predicted noise tensor of shape [B, 3, 32, 32].
        """
        t_emb = self.time_embed(t)

        h = self.input_conv(x)
        skips: List[torch.Tensor] = []

        for level, stage in enumerate(self.down_stages):
            for block, attention in stage:
                h = block(h, t_emb)
                h = attention(h)
                skips.append(h)

            if level != len(self.down_stages) - 1:
                h = self.downsamples[level](h)
                skips.append(h)

        h = self.mid_block1(h, t_emb)
        h = self.mid_attn(h)
        h = self.mid_block2(h, t_emb)

        for level, stage in enumerate(self.up_stages):
            for block, attention in stage:
                skip = skips.pop()
                h = torch.cat([h, skip], dim=1)
                h = block(h, t_emb)
                h = attention(h)

            if level != len(self.up_stages) - 1:
                h = self.upsamples[level](h)

        h = self.output_conv(self.output_act(self.output_norm(h)))
        return h
