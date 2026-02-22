#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/download_kaggle_dataset.sh
# Optional env overrides:
#   KAGGLE_DATASET_SLUG
#   TRAINING_DATA_DIR
#   KAGGLE_UNZIP (true|false)

KAGGLE_DATASET_SLUG="${KAGGLE_DATASET_SLUG:-shivamardeshna/real-and-fake-images-dataset-for-image-forensics}"
TRAINING_DATA_DIR="${TRAINING_DATA_DIR:-data/raw/image_forensics}"
KAGGLE_UNZIP="${KAGGLE_UNZIP:-true}"

if ! command -v kaggle >/dev/null 2>&1; then
  echo "[ERROR] Kaggle CLI not found. Install with: pip install kaggle"
  exit 1
fi

if [[ ! -f "${HOME}/.kaggle/kaggle.json" ]]; then
  echo "[ERROR] Missing Kaggle API key file: ${HOME}/.kaggle/kaggle.json"
  echo "Download API credentials from Kaggle account settings and place the file there."
  exit 1
fi

mkdir -p "${TRAINING_DATA_DIR}"

echo "Downloading dataset: ${KAGGLE_DATASET_SLUG}"
kaggle datasets download -d "${KAGGLE_DATASET_SLUG}" -p "${TRAINING_DATA_DIR}"

if [[ "${KAGGLE_UNZIP}" == "true" ]]; then
  zip_file="$(find "${TRAINING_DATA_DIR}" -maxdepth 1 -type f -name '*.zip' | head -n 1 || true)"
  if [[ -n "${zip_file}" ]]; then
    echo "Extracting: ${zip_file}"
    unzip -o "${zip_file}" -d "${TRAINING_DATA_DIR}"
  fi
fi

echo "Dataset ready in: ${TRAINING_DATA_DIR}"
