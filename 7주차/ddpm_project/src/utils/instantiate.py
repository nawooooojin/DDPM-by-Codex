from __future__ import annotations

from typing import Any, List

from hydra.utils import instantiate



def instantiate_from_cfg(cfg: Any, **kwargs: Any) -> Any:
    return instantiate(cfg, **kwargs)



def instantiate_callbacks(callback_cfg: Any) -> List[Any]:
    if callback_cfg is None:
        return []

    callbacks = []
    for cb in callback_cfg.get("callbacks", []):
        callbacks.append(instantiate(cb))
    return callbacks
