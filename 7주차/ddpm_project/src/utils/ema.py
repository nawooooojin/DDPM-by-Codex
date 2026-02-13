"""Exponential moving average utility for model weights."""

from __future__ import annotations

from typing import Dict, Optional

import torch
from torch import nn


class ModelEMA:
    """Track exponential moving averages of model parameters."""

    def __init__(self, model: nn.Module, decay: float) -> None:
        """Initialize EMA tracker.

        Args:
            model: Model to track.
            decay: Exponential decay factor.
        """
        self.decay = decay
        self.shadow: Dict[str, torch.Tensor] = {
            name: param.detach().clone() for name, param in model.named_parameters() if param.requires_grad
        }
        self.backup: Dict[str, torch.Tensor] = {}

    def update(self, model: nn.Module) -> None:
        """Update EMA weights from current model parameters.

        Args:
            model: Source model.
        """
        for name, param in model.named_parameters():
            if not param.requires_grad:
                continue
            self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def store(self, model: nn.Module) -> None:
        """Store current model parameters before applying EMA.

        Args:
            model: Target model.
        """
        self.backup = {
            name: param.detach().clone() for name, param in model.named_parameters() if param.requires_grad
        }

    def copy_to(self, model: nn.Module) -> None:
        """Copy EMA parameters to model.

        Args:
            model: Target model.
        """
        for name, param in model.named_parameters():
            if not param.requires_grad:
                continue
            param.data.copy_(self.shadow[name].data)

    def restore(self, model: nn.Module) -> None:
        """Restore model parameters saved by store().

        Args:
            model: Target model.
        """
        if not self.backup:
            return
        for name, param in model.named_parameters():
            if not param.requires_grad:
                continue
            param.data.copy_(self.backup[name].data)
        self.backup = {}

    def state_dict(self) -> Dict[str, torch.Tensor]:
        """Return EMA state dictionary.

        Returns:
            EMA shadow parameters.
        """
        return {name: tensor.clone() for name, tensor in self.shadow.items()}

    def load_state_dict(self, state_dict: Dict[str, torch.Tensor]) -> None:
        """Load EMA state dictionary.

        Args:
            state_dict: Serialized EMA state.
        """
        self.shadow = {name: tensor.clone() for name, tensor in state_dict.items()}
