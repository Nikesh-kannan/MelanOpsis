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
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    _, mask = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
    inpainted = cv2.inpaint(cv_img, mask, inpaintRadius=2, flags=cv2.INPAINT_TELEA)
    
    lab = cv2.cvtColor(inpainted, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced_lab = cv2.merge((cl, a, b))
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    return enhanced_bgr


class BenignMalignantDataset(Dataset):
    """
    PyTorch Dataset for Benign Moles vs Malignant Melanoma classification.
    Supports 11,879 images with OpenCV preprocessing & data augmentations.
    """
    def __init__(self, df: pd.DataFrame, transform=None, preprocess: bool = True):
        self.df = df.reset_index(drop=True)
        self.transform = transform
        self.preprocess = preprocess

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = row['filepath']
        label = float(row['label']) # 1.0 = Malignant Melanoma, 0.0 = Benign Mole
        
        if self.preprocess:
            cv_img = cv2.imread(img_path)
            if cv_img is None:
                # Fallback to PIL if OpenCV imread returns None
                image = Image.open(img_path).convert('RGB')
            else:
                cleaned_bgr = remove_hair_and_enhance(cv_img)
                rgb_img = cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(rgb_img)
        else:
            image = Image.open(img_path).convert('RGB')
            
        if self.transform:
            image = self.transform(image)
            
        return image, torch.tensor(label, dtype=torch.float32)


def get_benign_malignant_transforms(image_size: int = 224):
    """
    Returns train and val transform compositions with high-capacity augmentations.
    """
    train_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=30),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15, hue=0.03),
        transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.95, 1.05)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    return train_transform, val_transform
