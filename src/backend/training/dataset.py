import os
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset
from torchvision import transforms

# Mapping of HAM10000 diagnostic categories to binary risk classes
# High Risk (1): Melanoma (mel), Basal Cell Carcinoma (bcc), Actinic Keratoses (akiec)
# Low Risk (0): Melanocytic Nevi (nv), Benign Keratosis (bkl), Dermatofibroma (df), Vascular Lesions (vasc)
DIAGNOSTIC_MAPPING = {
    'mel': 1,   # Melanoma
    'bcc': 1,   # Basal cell carcinoma
    'akiec': 1, # Actinic keratoses / Bowen's disease
    'nv': 0,    # Melanocytic nevi
    'bkl': 0,   # Benign keratosis-like lesions
    'df': 0,    # Dermatofibroma
    'vasc': 0   # Vascular lesions
}

class HAM10000Dataset(Dataset):
    """
    Dataset loader for HAM10000 dermatoscopic images.
    Expects metadata CSV with columns ['image_id', 'dx'] and image directory path.
    """
    def __init__(self, df: pd.DataFrame, img_dir: str, transform=None):
        self.df = df.reset_index(drop=True)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        image_id = row['image_id']
        dx = row['dx']
        
        # Binary target label
        label = DIAGNOSTIC_MAPPING.get(dx, 0)
        
        # Locate image file (could end in .jpg or .png)
        img_filename = f"{image_id}.jpg"
        img_path = os.path.join(self.img_dir, img_filename)
        
        if not os.path.exists(img_path):
            # Fallback search if organized in subfolders
            for root, _, files in os.walk(self.img_dir):
                if img_filename in files:
                    img_path = os.path.join(root, img_filename)
                    break
        
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
            
        return image, torch.tensor(label, dtype=torch.float32)


def get_transforms():
    """
    Returns train and val transform compositions with dermatoscopic data augmentations.
    """
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=30),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    return train_transform, val_transform
