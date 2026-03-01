from __future__ import annotations

from typing import Any, Optional

import lightning as L
import torch
from torch import nn


class LitClassifier(L.LightningModule):
    """LightningModule wrapper for the toy config-driven baseline."""

    def __init__(
        self,
        net: nn.Module,
        lr: float,
        weight_decay: float,
        num_classes: int,
    ) -> None:
        super().__init__()
        self.save_hyperparameters(ignore=["net"])
        self.net = net
        self.criterion = nn.CrossEntropyLoss()
        self.latest_train_loss: Optional[float] = None
        self.num_classes = num_classes

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    def _shared_step(self, batch: Any, stage: str) -> torch.Tensor:
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()

        self.log(f"{stage}_loss", loss, prog_bar=(stage != "train"), on_step=True, on_epoch=True)
        self.log(f"{stage}_acc", acc, prog_bar=(stage != "train"), on_step=True, on_epoch=True)
        return loss

    def training_step(self, batch: Any, batch_idx: int) -> torch.Tensor:
        loss = self._shared_step(batch, stage="train")
        self.latest_train_loss = float(loss.detach().cpu().item())
        return loss

    def validation_step(self, batch: Any, batch_idx: int) -> torch.Tensor:
        return self._shared_step(batch, stage="val")

    def test_step(self, batch: Any, batch_idx: int) -> torch.Tensor:
        return self._shared_step(batch, stage="test")

    def predict_step(self, batch: Any, batch_idx: int, dataloader_idx: int = 0) -> torch.Tensor:
        x, _ = batch
        logits = self(x)
        return torch.argmax(logits, dim=1)

    def configure_optimizers(self) -> torch.optim.Optimizer:
        return torch.optim.AdamW(self.parameters(), lr=self.hparams.lr, weight_decay=self.hparams.weight_decay)
