from pathlib import Path

from hydra import compose, initialize_config_dir



def test_toy_experiment_paper_repro_composes() -> None:
    config_dir = Path(__file__).resolve().parents[1] / "configs"
    with initialize_config_dir(version_base="1.3", config_dir=str(config_dir)):
        cfg = compose(config_name="train_toy", overrides=["experiment=paper_repro"])

    assert int(cfg.seed) == 123
    assert int(cfg.trainer.max_epochs) == 10



def test_toy_experiment_ablation_composes() -> None:
    config_dir = Path(__file__).resolve().parents[1] / "configs"
    with initialize_config_dir(version_base="1.3", config_dir=str(config_dir)):
        cfg = compose(config_name="train_toy", overrides=["experiment=ablation_example"])

    assert int(cfg.model.net.hidden_dim) == 32
    assert float(cfg.data.noise_std) == 1.0
