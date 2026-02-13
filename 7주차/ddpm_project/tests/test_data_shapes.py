"""Tests for CIFAR-10 dataloader shapes and value range."""

from __future__ import annotations

import torch

from src.data.cifar10 import create_dataloaders


def test_data_shapes_and_range() -> None:
    """Validate dataloader output shape and normalization range."""
    train_loader, _ = create_dataloaders(
        root="data",
        batch_size=8,
        num_workers=0,
        pin_memory=False,
        use_fake_data=True,
        overfit_one_batch=False,
    )

    images, labels = next(iter(train_loader))

    assert images.shape == (8, 3, 32, 32)
    assert labels.shape == (8,)
    assert images.dtype == torch.float32
    assert float(images.min()) >= -1.1
    assert float(images.max()) <= 1.1
