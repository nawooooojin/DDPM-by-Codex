__all__ = []

try:
    from src.data.toy_datamodule import ToyClassificationDataModule

    __all__.append("ToyClassificationDataModule")
except ModuleNotFoundError:
    # Optional toy/lightning components may be unavailable in minimal DDPM envs.
    pass
