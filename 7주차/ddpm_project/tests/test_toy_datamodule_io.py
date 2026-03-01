import torch

from src.data import ToyClassificationDataModule



def test_datamodule_batch_io() -> None:
    dm = ToyClassificationDataModule(
        batch_size=16,
        num_workers=0,
        input_dim=12,
        num_classes=3,
        train_size=64,
        val_size=32,
        test_size=32,
        noise_std=0.5,
        seed=7,
    )

    dm.prepare_data()
    dm.setup("fit")
    x, y = next(iter(dm.train_dataloader()))

    assert isinstance(x, torch.Tensor)
    assert isinstance(y, torch.Tensor)
    assert x.shape[1] == 12
    assert y.dtype == torch.long
