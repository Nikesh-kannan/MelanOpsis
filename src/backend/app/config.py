import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Storage paths
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
DB_PATH = DATA_DIR / "dermscani.db"
# Model paths
BENIGN_MALIGNANT_MODEL_PATH = BASE_DIR / "app" / "models" / "efficientnet_b0_benign_malignant.pt"
MELANOMA_MODEL_PATH = BASE_DIR / "app" / "models" / "efficientnet_b0_melanoma.pt"
HAM10000_MODEL_PATH = BASE_DIR / "models" / "efficientnet_b0_ham10000.pt"

def get_model_path():
    if BENIGN_MALIGNANT_MODEL_PATH.exists():
        return BENIGN_MALIGNANT_MODEL_PATH
    alt_bm = BASE_DIR / "models" / "efficientnet_b0_benign_malignant.pt"
    if alt_bm.exists():
        return alt_bm
    if MELANOMA_MODEL_PATH.exists():
        return MELANOMA_MODEL_PATH
    alt_melanoma = BASE_DIR / "models" / "efficientnet_b0_melanoma.pt"
    if alt_melanoma.exists():
        return alt_melanoma
    return HAM10000_MODEL_PATH

MODEL_PATH = get_model_path()

# Ensure directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "models").mkdir(parents=True, exist_ok=True)

# Application settings
APP_NAME = "DermScanI API"
VERSION = "1.0.0"
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

# Triage configuration
HIGH_RISK_THRESHOLD = 0.40  # Sensitive threshold for high risk detection (prioritizes recall)
IMAGE_INPUT_SIZE = (224, 224)
