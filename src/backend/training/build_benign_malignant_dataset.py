import os
import glob
import pandas as pd

BENIGN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Benign"))
MALIGNANT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Malignant"))
OUTPUT_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "benign_malignant_metadata.csv"))

def generate_benign_malignant_metadata():
    benign_files = sorted(glob.glob(os.path.join(BENIGN_DIR, "*.jpg")) + glob.glob(os.path.join(BENIGN_DIR, "*.png")))
    malignant_files = sorted(glob.glob(os.path.join(MALIGNANT_DIR, "*.jpg")) + glob.glob(os.path.join(MALIGNANT_DIR, "*.png")))
    
    print(f"[DatasetBuilder] Found {len(benign_files)} Benign images in {BENIGN_DIR}")
    print(f"[DatasetBuilder] Found {len(malignant_files)} Malignant images in {MALIGNANT_DIR}")
    
    records = []
    for filepath in benign_files:
        filename = os.path.basename(filepath)
        image_id = os.path.splitext(filename)[0]
        records.append({
            'image_id': f"benign_{image_id}",
            'filename': filename,
            'filepath': filepath,
            'dx': 'nv', # Benign Mole / Nevus
            'label': 0
        })
        
    for filepath in malignant_files:
        filename = os.path.basename(filepath)
        image_id = os.path.splitext(filename)[0]
        records.append({
            'image_id': f"malignant_{image_id}",
            'filename': filename,
            'filepath': filepath,
            'dx': 'mel', # Malignant Melanoma / Cancer
            'label': 1
        })
        
    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    
    print(f"[DatasetBuilder] Created metadata CSV at {OUTPUT_CSV}")
    print(f"[DatasetBuilder] Summary: Total: {len(df)} | Benign Moles (0): {len(benign_files)} | Malignant Melanoma (1): {len(malignant_files)}")
    return df

if __name__ == "__main__":
    generate_benign_malignant_metadata()
