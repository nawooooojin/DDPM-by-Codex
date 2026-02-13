"""Tests for UNet interface and output contract."""

from __future__ import annotations

import torch

from src.models.unet import UNet


def test_unet_forward_shape_dtype() -> None:
    """UNet should return epsilon prediction with input-compatible shape."""
    model = UNet(
        in_channels=3,
        out_channels=3,
        base_channels=64,
        channel_mult=[1, 2, 2],
        num_res_blocks=2,
        attn_resolutions=[16],
        dropout=0.1,
        image_size=32,
    )

    x = torch.randn(4, 3, 32, 32)
    t = torch.randint(0, 1000, (4,), dtype=torch.long)

    out = model(x, t)

    assert out.shape == x.shape
    assert out.dtype == x.dtype
