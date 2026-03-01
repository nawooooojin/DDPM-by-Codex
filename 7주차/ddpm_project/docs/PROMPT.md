# PROMPT

## Goals
- Maintain reproducible, extensible DL research artifact with Hydra-centered configuration.
- Preserve DDPM pipeline while adding reusable sanity/research scaffolding.
- Prevent agent drift via durable markdown memory.

## Non-Goals
- One-off scripts with hidden constants.
- Notebook-only production logic.

## Constraints
- Use `src` package layout and orchestration-only `scripts`.
- Keep experiment knobs in `configs/`.
- Keep outputs out of git history.

## Deliverables
- DDPM + toy pipelines coexisting in one repo.
- Hydra config groups and experiment templates.
- Sanity-check/report automation entrypoints.
- Skills/automation/safety policy files.

## Done-When
- Mandatory folders/files exist in `ddpm_project`.
- Config-driven instantiate path works.
- README explains install/run/add-experiment.
- STATUS records validation outcomes.
