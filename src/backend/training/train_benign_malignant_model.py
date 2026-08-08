import os
import sys
import argparse
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.network import DermScanNet
from training.benign_malignant_dataset import BenignMalignantDataset, get_benign_malignant_transforms
from training.build_benign_malignant_dataset import generate_benign_malignant_metadata

METADATA_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "benign_malignant_metadata.csv"))
MODEL_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "models"))


def train_benign_malignant_classifier(epochs: int = 10, batch_size: int = 32, lr: float = 1e-4, resume: bool = False, resume_checkpoint: str = None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n=======================================================")
    print(f"  BENIGN VS MALIGNANT (MELANOMA) PYTORCH DEEP LEARNING  ")
    print(f"  Device: {device} | CUDA Available: {torch.cuda.is_available()}")
    print(f"=======================================================\n")
    
    # 1. Ensure Metadata CSV exists
    if not os.path.exists(METADATA_CSV):
        print(f"[Setup] Metadata CSV not found. Generating...")
        df = generate_benign_malignant_metadata()
    else:
        df = pd.read_csv(METADATA_CSV)
        
    num_benign = (df['label'] == 0).sum()
    num_malignant = (df['label'] == 1).sum()
    print(f"[Dataset] Total Samples: {len(df)} | Benign Moles (0): {num_benign} | Malignant Melanoma (1): {num_malignant}")
    
    # 2. Class Imbalance Weighting
    pos_weight_val = torch.tensor([float(num_benign) / float(num_malignant)], dtype=torch.float32).to(device)
    print(f"[Loss Weighting] Computed BCE pos_weight: {pos_weight_val.item():.2f}")
    
    # 3. Stratified 80/10/10 Train / Val / Test Split
    train_df, test_df = train_test_split(df, test_size=0.20, stratify=df['label'], random_state=42)
    val_df, test_df = train_test_split(test_df, test_size=0.50, stratify=test_df['label'], random_state=42)
    
    print(f"[Data Split] Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")
    
    # 4. Data Transforms & Loaders
    train_transform, val_transform = get_benign_malignant_transforms()
    
    train_dataset = BenignMalignantDataset(train_df, transform=train_transform, preprocess=True)
    val_dataset = BenignMalignantDataset(val_df, transform=val_transform, preprocess=True)
    test_dataset = BenignMalignantDataset(test_df, transform=val_transform, preprocess=True)
    
    num_workers = 2 if os.name != 'nt' else 0
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    
    # 5. Initialize Pre-trained Neural Network
    model = DermScanNet(pretrained=True).to(device)
    
    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
    best_model_path = os.path.join(MODEL_OUTPUT_DIR, "efficientnet_b0_benign_malignant.pt")
    
    # Checkpoint Resuming
    ckpt_path = resume_checkpoint if resume_checkpoint else best_model_path
    if resume or (resume_checkpoint and os.path.exists(resume_checkpoint)):
        if os.path.exists(ckpt_path):
            try:
                state_dict = torch.load(ckpt_path, map_location=device)
                model.load_state_dict(state_dict)
                print(f"[Resume] Successfully loaded checkpoint weights from: {ckpt_path}")
            except Exception as e:
                print(f"[Resume Warning] Could not load checkpoint ({e}). Training from backbone defaults.")
        else:
            print(f"[Resume Warning] Checkpoint file not found at {ckpt_path}. Training from backbone defaults.")
            
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight_val)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    
    best_val_loss = float('inf')
    
    # 6. Training Loop
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            logits = model.backbone(images).squeeze(1)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            
        epoch_train_loss = running_loss / len(train_dataset)
        
        # Validation Pass
        model.eval()
        val_loss = 0.0
        all_labels = []
        all_preds = []
        all_probs = []
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)
                
                logits = model.backbone(images).squeeze(1)
                loss = criterion(logits, labels)
                val_loss += loss.item() * images.size(0)
                
                probs = torch.sigmoid(logits)
                preds = (probs >= 0.40).float()
                
                all_labels.extend(labels.cpu().numpy())
                all_preds.extend(preds.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())
                
        epoch_val_loss = val_loss / len(val_dataset)
        scheduler.step()
        
        acc = accuracy_score(all_labels, all_preds)
        sens = recall_score(all_labels, all_preds, zero_division=0)
        auc = roc_auc_score(all_labels, all_probs)
        
        print(f"Epoch {epoch+1:02d}/{epochs:02d} | Train Loss: {epoch_train_loss:.4f} | Val Loss: {epoch_val_loss:.4f} | Val Acc: {acc*100:.2f}% | Sensitivity: {sens*100:.2f}% | AUC: {auc:.4f}")
        
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            torch.save(model.state_dict(), best_model_path)
            print(f"   Saved best model checkpoint to {best_model_path}")
            
    # 7. Final Evaluation on Held-Out Test Set (1,188 images)
    print("\n=======================================================")
    print("   FINAL EVALUATION ON HELD-OUT TEST SET (1,188 IMAGES)  ")
    print("=======================================================")
    model.load_state_dict(torch.load(best_model_path))
    model.eval()
    
    test_labels, test_preds, test_probs = [], [], []
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            logits = model.backbone(images).squeeze(1)
            probs = torch.sigmoid(logits)
            preds = (probs >= 0.40).float()
            
            test_labels.extend(labels.cpu().numpy())
            test_preds.extend(preds.cpu().numpy())
            test_probs.extend(probs.cpu().numpy())
            
    test_acc = accuracy_score(test_labels, test_preds)
    test_sens = recall_score(test_labels, test_preds, zero_division=0)
    test_prec = precision_score(test_labels, test_preds, zero_division=0)
    test_f1 = f1_score(test_labels, test_preds, zero_division=0)
    test_auc = roc_auc_score(test_labels, test_probs)
    
    cm = confusion_matrix(test_labels, test_preds)
    tn, fp, fn, tp = cm.ravel()
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    print(f"Test Accuracy:      {test_acc * 100:.2f}%")
    print(f"Test Sensitivity:   {test_sens * 100:.2f}% (Malignant Melanoma Recall)")
    print(f"Test Specificity:   {spec * 100:.2f}% (Benign Mole Recall)")
    print(f"Test Precision:     {test_prec * 100:.2f}%")
    print(f"Test F1-Score:      {test_f1:.4f}")
    print(f"Test AUC-ROC Score: {test_auc:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"  True Benign Moles:       {tn} Correct (TN), {fp} False Alarms (FP)")
    print(f"  True Malignant Melanoma: {tp} Correct (TP), {fn} Missed (FN)")
    
    print("\nModel training & evaluation successfully completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Benign vs Malignant PyTorch Classifier")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--resume", action="store_true", help="Resume training from the existing saved model checkpoint")
    parser.add_argument("--resume_checkpoint", type=str, default=None, help="Explicit file path to checkpoint file to resume from")
    args = parser.parse_args()
    
    train_benign_malignant_classifier(
        epochs=args.epochs, 
        batch_size=args.batch_size, 
        lr=args.lr,
        resume=args.resume,
        resume_checkpoint=args.resume_checkpoint
    )
