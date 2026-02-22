# Training Data Sources

## Image Deepfake / Forensics Dataset (Primary)

- Platform: Kaggle
- Dataset: `shivamardeshna/real-and-fake-images-dataset-for-image-forensics`
- URL: https://www.kaggle.com/datasets/shivamardeshna/real-and-fake-images-dataset-for-image-forensics
- Usage: Primary image training/evaluation source for real-vs-fake image classification.

## Notes

- Keep train/validation/test splits deterministic.
- Preserve class balance checks before model training.
- Track dataset version/date in experiment metadata for reproducibility.
