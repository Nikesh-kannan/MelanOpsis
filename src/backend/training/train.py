import os
import argparse
import sys
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Add parent directory to path for app imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.network import DermScanNet
from training.dataset import HAM10000Dataset, get_transforms, DIAGNOSTIC_MAPPING

def train_model(data_dir: str, metadata_csv: str, epochs: int = 10, batch_size: int = 32, lr: float = 1e-4, output_dir: str = "../app/models"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train] Training DermScanI on device: {device}")
    
    if not os.path.exists(metadata_csv):
        print(f"[Error] Metadata file not found at: {metadata_csv}")
        return

    # Load HAM10000 Metadata
    df = pd.read_csv(metadata_csv)
    df['binary_label'] = df['dx'].map(lambda x: DIAGNOSTIC_MAPPING.get(x, 0))
    
    num_high_risk = (df['binary_label'] == 1).sum()
    num_low_risk = (df['binary_label'] == 0).sum()
    print(f"[Dataset] Total samples: {len(df)} | Low-Risk: {num_low_risk} | High-Risk: {num_high_risk}")
    
    # Calculate pos_weight to handle class imbalance
    pos_weight_val = torch.tensor([num_low_risk / float(num_high_risk)], dtype=torch.float32).to(device)
    print(f"[Class Balance] Computed pos_weight: {pos_weight_val.item():.2f}")
    
    # Stratified Train/Val/Test Split (70% train, 15% val, 15% test)
    train_df, test_df = train_test_split(df, test_size=0.3, stratify=df['binary_label'], random_state=42)
    val_df, test_df = train_test_split(test_df, test_size=0.5, stratify=test_df['binary_label'], random_state=42)
    
    print(f"[Split] Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")
    
    train_transform, val_transform = get_transforms()
    
    train_dataset = HAM10000Dataset(train_df, data_dir, transform=train_transform)
    val_dataset = HAM10000Dataset(val_df, data_dir, transform=val_transform)
    test_dataset = HAM10000Dataset(test_df, data_dir, transform=val_transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    # Initialize Model & Loss
    model = DermScanNet(pretrained=True).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight_val)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-3)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2)
    
    best_val_loss = float('inf')
    os.makedirs(output_dir, exist_ok=True)
    best_model_path = os.path.join(output_dir, "efficientnet_b0_ham10000.pt")
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            # Note: DermScanNet forward returns sigmoid probabilities, for BCEWithLogitsLoss we use raw logits
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
                preds = (probs >= 0.40).float() # Sensitive triage threshold
                
                all_labels.extend(labels.cpu().numpy())
                all_preds.extend(preds.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())
                
        epoch_val_loss = val_loss / len(val_dataset)
        scheduler.step(epoch_val_loss)
        
        sensitivity = recall_score(all_labels, all_preds, zero_division=0)
        acc = accuracy_score(all_labels, all_preds)
        auc = roc_auc_score(all_labels, all_probs)
        
        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {epoch_train_loss:.4f} | Val Loss: {epoch_val_loss:.4f} | Val Acc: {acc:.4f} | Sensitivity (Recall): {sensitivity:.4f} | AUC: {auc:.4f}")
        
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            torch.save(model.state_dict(), best_model_path)
            print(f" Saved best model weights to {best_model_path}")

    # Evaluate on Test Set
    print("\n--- Final Evaluation on Test Set ---")
    model.load_state_dict(torch.load(best_model_path))
    model.eval()
    
    test_labels, test_preds, test_probs = [], [], []
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            probs = model(images).squeeze(1)
            preds = (probs >= 0.40).float()
            
            test_labels.extend(labels.cpu().numpy())
            test_preds.extend(preds.cpu().numpy())
            test_probs.extend(probs.cpu().numpy())
            
    print(f"Test Accuracy:      {accuracy_score(test_labels, test_preds):.4f}")
    print(f"Test Sensitivity:   {recall_score(test_labels, test_preds):.4f} (Recall on High-Risk class)")
    print(f"Test Precision:     {precision_score(test_labels, test_preds, zero_division=0):.4f}")
    print(f"Test F1-Score:      {f1_score(test_labels, test_preds, zero_division=0):.4f}")
    print(f"Test AUC-ROC:       {roc_auc_score(test_labels, test_probs):.4f}")
    
    # Export to TorchScript
    print("\nExporting model to TorchScript format...")
    try:
        scripted_model = torch.jit.script(model)
        torchscript_path = os.path.join(output_dir, "efficientnet_b0_ham10000_torchscript.pt")
        scripted_model.save(torchscript_path)
        print(f" Saved TorchScript model to {torchscript_path}")
    except Exception as e:
        print(f"TorchScript export skipped: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train DermScanI EfficientNet-B0 skin triage model.")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to directory containing HAM10000 images")
    parser.add_argument("--metadata_csv", type=str, required=True, help="Path to HAM10000_metadata.csv")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    args = parser.parse_args()
    
    train_model(args.data_dir, args.metadata_csv, args.epochs, args.batch_size, args.lr)
