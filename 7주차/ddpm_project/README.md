# DDPM Study Project (Week 7)

Pure PyTorch + Hydra + WandB implementation for DDPM training and DDPM/DDIM comparison on CIFAR-10.

## 1) Environment setup

```bash
cd "7주차/ddpm_project"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Sanity checks

The project includes custom replacements for Lightning sanity features:

1. Theoretical Loss Check: printed at training step 1.
2. Overfit One Batch:

```bash
python scripts/train.py runtime.overfit_one_batch=true runtime.total_steps=1000 runtime.sample_every=200 logging.use_wandb=false
```

3. Fast Dev Run:

```bash
python scripts/train.py runtime.fast_dev_run=true logging.use_wandb=false
```

## 3) Train

```bash
python scripts/train.py logging.use_wandb=true
```

Sampler switch is Hydra-only:

```bash
python scripts/train.py sampler=ddpm
python scripts/train.py sampler=ddim
```

## 3-1) M1 Pro quick preset (recommended)

Use smaller model, fewer diffusion steps, and MPS device:

```bash
python scripts/train.py model=unet_m1_small data=cifar10_m1 diffusion=ddpm_m1 runtime=m1_quick logging.use_wandb=false
```

For faster DDIM visual comparison on M1:

```bash
python scripts/eval.py model=unet_m1_small diffusion=ddpm_m1 sampler=ddim_m1 runtime=m1_quick runtime.checkpoint_path=/absolute/path/to/last.pt logging.use_wandb=false
```

## 4) Evaluate from checkpoint

```bash
python scripts/eval.py runtime.checkpoint_path=/absolute/path/to/last.pt logging.use_wandb=false
```

## 5) Expected outputs

Run artifacts are stored under Hydra run directory:

- `checkpoints/step_*.pt`, `checkpoints/last.pt`
- `figures/noise_schedule_curves.png`
- `figures/forward_noising_grid.png`
- `figures/reverse_trajectory_ddpm.png`
- `figures/reverse_trajectory_ddim.png`
- `figures/ddpm_vs_ddim_samples.png`
- `figures/train_loss_curve.png`
- `resolved_config.yaml`, `run_metadata.txt`
