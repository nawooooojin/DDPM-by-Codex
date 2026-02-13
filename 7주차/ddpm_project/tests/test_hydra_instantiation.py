"""Tests for Hydra-based component instantiation."""

from __future__ import annotations

from hydra.utils import instantiate
from omegaconf import OmegaConf


def test_hydra_instantiates_model_diffusion_and_data() -> None:
    """Hydra should instantiate configured targets without hardcoded branching."""
    model_cfg = OmegaConf.create(
        {
            "_target_": "src.models.unet.UNet",
            "in_channels": 3,
            "out_channels": 3,
            "base_channels": 32,
            "channel_mult": [1, 2],
            "num_res_blocks": 1,
            "attn_resolutions": [16],
            "dropout": 0.1,
            "image_size": 32,
        }
    )
    diffusion_cfg = OmegaConf.create(
        {
            "_target_": "src.models.diffusion.GaussianDiffusion",
            "num_timesteps": 100,
            "beta_schedule": "linear",
            "beta_start": 1e-4,
            "beta_end": 2e-2,
            "objective": "epsilon",
        }
    )
    data_cfg = OmegaConf.create(
        {
            "_target_": "src.data.cifar10.create_dataloaders",
            "root": "data",
            "batch_size": 4,
            "num_workers": 0,
            "pin_memory": False,
            "use_fake_data": True,
            "download": False,
            "overfit_one_batch": False,
        }
    )

    model = instantiate(model_cfg)
    diffusion = instantiate(diffusion_cfg)
    train_loader, val_loader = instantiate(data_cfg)

    assert model is not None
    assert diffusion is not None
    assert train_loader is not None
    assert val_loader is not None
