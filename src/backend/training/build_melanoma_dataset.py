import os
import glob
import pandas as pd
import numpy as np

MELANOMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "melanoma"))
OUTPUT_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "melanoma_metadata.csv"))

# ISIC 2016 standard ground truth melanoma labels (1 = Melanoma, 0 = Mole / Benign Nevus)
MELANOMA_ISIC_IDS = {
    'ISIC_0000139', 'ISIC_0000150', 'ISIC_0000157', 'ISIC_0000159', 'ISIC_0000160',
    'ISIC_0000173', 'ISIC_0000175', 'ISIC_0000279', 'ISIC_0000288', 'ISIC_0000293',
    'ISIC_0000298', 'ISIC_0000305', 'ISIC_0000311', 'ISIC_0000394', 'ISIC_0000400',
    'ISIC_0000405', 'ISIC_0000412', 'ISIC_0000417', 'ISIC_0000440', 'ISIC_0000445',
    'ISIC_0000469', 'ISIC_0000511', 'ISIC_0000517', 'ISIC_0000522', 'ISIC_0000533',
    'ISIC_0000547', 'ISIC_0000551', 'ISIC_0000553', 'ISIC_0000555',
    'ISIC_0009886', 'ISIC_0009918', 'ISIC_0009934', 'ISIC_0009960', 'ISIC_0009989',
    'ISIC_0010007', 'ISIC_0010016', 'ISIC_0010023', 'ISIC_0010034', 'ISIC_0010049',
    'ISIC_0010056', 'ISIC_0010080', 'ISIC_0010094', 'ISIC_0010131', 'ISIC_0010143',
    'ISIC_0010162', 'ISIC_0010174', 'ISIC_0010194', 'ISIC_0010210', 'ISIC_0010240',
    'ISIC_0010251', 'ISIC_0010283', 'ISIC_0010319', 'ISIC_0010355', 'ISIC_0010360',
    'ISIC_0010376', 'ISIC_0010385', 'ISIC_0010398', 'ISIC_0010414', 'ISIC_0010469',
    'ISIC_0010486', 'ISIC_0010534', 'ISIC_0010548', 'ISIC_0010580', 'ISIC_0010596',
    'ISIC_0010611', 'ISIC_0010652', 'ISIC_0010719', 'ISIC_0010729', 'ISIC_0010754',
    'ISIC_0010777', 'ISIC_0010784', 'ISIC_0010791', 'ISIC_0010797', 'ISIC_0010809',
    'ISIC_0010860', 'ISIC_0010872', 'ISIC_0010890', 'ISIC_0010909', 'ISIC_0010925',
    'ISIC_0010977', 'ISIC_0010993', 'ISIC_0011031', 'ISIC_0011040', 'ISIC_0011045',
    'ISIC_0011057', 'ISIC_0011095', 'ISIC_0011125', 'ISIC_0011135', 'ISIC_0011137',
    'ISIC_0011139', 'ISIC_0011158', 'ISIC_0011166', 'ISIC_0011176', 'ISIC_0011181',
    'ISIC_0011193'
}

def generate_melanoma_metadata():
    image_files = sorted(glob.glob(os.path.join(MELANOMA_DIR, "*.jpg")))
    print(f"[DatasetBuilder] Found {len(image_files)} images in {MELANOMA_DIR}")
    
    records = []
    for filepath in image_files:
        filename = os.path.basename(filepath)
        image_id = os.path.splitext(filename)[0]
        
        # Binary target: 1 = Melanoma, 0 = Mole / Benign Nevus
        is_melanoma = 1 if image_id in MELANOMA_ISIC_IDS else 0
        records.append({
            'image_id': image_id,
            'filename': filename,
            'dx': 'mel' if is_melanoma == 1 else 'nv',
            'label': is_melanoma
        })
        
    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    
    num_melanoma = (df['label'] == 1).sum()
    num_mole = (df['label'] == 0).sum()
    print(f"[DatasetBuilder] Created {OUTPUT_CSV}")
    print(f"[DatasetBuilder] Summary: Total: {len(df)} | Melanoma (1): {num_melanoma} | Mole/Nevus (0): {num_mole}")
    return df

if __name__ == "__main__":
    generate_melanoma_metadata()
