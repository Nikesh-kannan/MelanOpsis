import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset
from torchvision import transforms

def remove_hair_and_enhance(cv_img: np.ndarray) -> np.ndarray:
    """
    OpenCV preprocessing pipeline for dermatoscopic skin images:
    1. Blackhat Morphological Filtering + Inpainting for Hair Removal.
    2. CLAHE (Contrast Limited Adaptive Histogram Equalization) on LAB L-channel.
    """
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    
    # 1. Morphological Blackhat filtering to highlight thin dark structures (hair)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    
    # Threshold mask
    _, mask = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
    
    # Telea Inpainting to remove hair pixels smoothly
    inpainted = cv2.inpaint(cv_img, mask, 1, cv2.INPAINT_TELEA)
    
    # 2. CLAHE contrast enhancement on LAB L-channel
    lab = cv2.cvtColor(inpainted, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced_lab = cv2.merge((cl, a, b))
    
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    return enhanced_bgr


class MelanomaDataset(Dataset):
    """
    PyTorch Dataset for Melanoma vs Mole binary classification.
    Applies OpenCV hair removal & CLAHE preprocessing, followed by PyTorch augmentations.
    """
    def __init__(self, df: pd.DataFrame, img_dir: str, transform=None, preprocess: bool = True):
        self.df = df.reset_index(drop=True)
        self.img_dir = img_dir
        self.transform = transform
        self.preprocess = preprocess

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        filename = row['filename']
        label = float(row['label']) # 1.0 for Melanoma, 0.0 for Mole
        
        img_path = os.path.join(self.img_dir, filename)
        
        if self.preprocess:
            cv_img = cv2.imread(img_path)
            if cv_img is None:
                raise FileNotFoundError(f"Image not found at {img_path}")
            cleaned_bgr = remove_hair_and_enhance(cv_img)
            rgb_img = cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb_img)
        else:
            image = Image.open(img_path).convert('RGB')
            
        if self.transform:
            image = self.transform(image)
            
        return image, torch.tensor(label, dtype=torch.float32)


def get_melanoma_transforms(image_size: int = 224):
    """
    Returns train and val transform compositions with heavy dermatoscopic augmentations.
    """
    train_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=45),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.RandomAffine(degrees=0, translate=(0.08, 0.08), scale=(0.9, 1.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    return train_transform, val_transform
