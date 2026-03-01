from pathlib import Path

from hydra import compose, initialize_config_dir
from hydra.utils import instantiate



def test_hydra_instantiate_toy_model_data_trainer() -> None:
    config_dir = Path(__file__).resolve().parents[1] / "configs"

    with initialize_config_dir(version_base="1.3", config_dir=str(config_dir)):
        cfg = compose(config_name="train_toy")

    model = instantiate(cfg.model)
    datamodule = instantiate(cfg.data)
    trainer = instantiate(cfg.trainer, callbacks=[])

    assert model is not None
    assert datamodule is not None
    assert trainer is not None
