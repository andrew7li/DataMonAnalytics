# DataMonAnalysis

This repository contains analysis on Pokemon TCG cards, specifically answering the question of "What actually drives the price of graded pokemon cards?"

## Project Structure

```text
analysis/
  scripts/          Reusable analysis and data-prep scripts
  outputs/          Saved EDA and regression text outputs
  plots/            Saved figures
data/
  raw/              Original TCG CSV exports
  processed/        Final modeling datasets
  intermediate/     Generated cleaning and merge artifacts
  external/         External fixture/reference data
```

## Main Datasets

- `data/processed/sv_modeling_dataset.csv`
- `data/processed/ex_era_dataset.csv`

## Reproducing Analysis

Set `DATASET = "sv"` or `DATASET = "ex_era"` near the top of the reusable scripts:

```bash
python analysis/scripts/run_eda.py
python analysis/scripts/run_regression.py
python analysis/scripts/ex_era_graphs.py
```
