from __future__ import annotations

from typing import Optional

import lightning as L
import torch
from torch.utils.data import DataLoader, TensorDataset


class ToyClassificationDataModule(L.LightningDataModule):
    """Synthetic classification DataModule with deterministic splits."""

    def __init__(
        self,
        batch_size: int,
        num_workers: int,
        input_dim: int,
        num_classes: int,
        train_size: int,
        val_size: int,
        test_size: int,
        noise_std: float,
        seed: int,
    ) -> None:
        super().__init__()
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.train_size = train_size
        self.val_size = val_size
        self.test_size = test_size
        self.noise_std = noise_std
        self.seed = seed

        self.train_dataset: Optional[TensorDataset] = None
        self.val_dataset: Optional[TensorDataset] = None
        self.test_dataset: Optional[TensorDataset] = None

    def prepare_data(self) -> None:
        return

    def _make_split(self, size: int, split_seed: int) -> TensorDataset:
        generator = torch.Generator().manual_seed(split_seed)
        centers = torch.randn(self.num_classes, self.input_dim, generator=generator) * 2.0
        labels = torch.randint(0, self.num_classes, (size,), generator=generator)
        features = centers[labels] + self.noise_std * torch.randn(size, self.input_dim, generator=generator)
        return TensorDataset(features.float(), labels.long())

    def setup(self, stage: Optional[str] = None) -> None:
        if stage in (None, "fit"):
            self.train_dataset = self._make_split(self.train_size, self.seed)
            self.val_dataset = self._make_split(self.val_size, self.seed + 1)

        if stage in (None, "test", "predict"):
            self.test_dataset = self._make_split(self.test_size, self.seed + 2)

    def train_dataloader(self) -> DataLoader:
        if self.train_dataset is None:
            raise RuntimeError("train_dataset is not initialized. Call setup('fit') first.")
        return DataLoader(self.train_dataset, batch_size=self.batch_size, num_workers=self.num_workers, shuffle=True)

    def val_dataloader(self) -> DataLoader:
        if self.val_dataset is None:
            raise RuntimeError("val_dataset is not initialized. Call setup('fit') first.")
        return DataLoader(self.val_dataset, batch_size=self.batch_size, num_workers=self.num_workers, shuffle=False)

    def test_dataloader(self) -> DataLoader:
        if self.test_dataset is None:
            raise RuntimeError("test_dataset is not initialized. Call setup('test') first.")
        return DataLoader(self.test_dataset, batch_size=self.batch_size, num_workers=self.num_workers, shuffle=False)

    def predict_dataloader(self) -> DataLoader:
        return self.test_dataloader()
