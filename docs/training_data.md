# Training Data Sources

## Image Deepfake / Forensics Dataset (Primary)

- Platform: Kaggle
- Dataset: `shivamardeshna/real-and-fake-images-dataset-for-image-forensics`
- URL: https://www.kaggle.com/datasets/shivamardeshna/real-and-fake-images-dataset-for-image-forensics
- Usage: Primary image training/evaluation source for real-vs-fake image classification.

## Download Workflow

1. Install Kaggle CLI:

```bash
pip install kaggle
```

2. Add Kaggle API credentials:
- Download `kaggle.json` from your Kaggle account settings.
- Place file at `~/.kaggle/kaggle.json`.

3. Download dataset into project data directory:

```bash
./scripts/download_kaggle_dataset.sh
```

Optional environment overrides:
- `KAGGLE_DATASET_SLUG`
- `TRAINING_DATA_DIR`
- `KAGGLE_UNZIP=true|false`

## Notes

- Keep train/validation/test splits deterministic.
- Preserve class balance checks before model training.
- Track dataset version/date in experiment metadata for reproducibility.
