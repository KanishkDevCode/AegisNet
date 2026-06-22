import os
import glob
import time
import math
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import json

# ==========================================================
# AegisNet Phase 2: Vision Triage (The Analyst)
# Upgraded ViT Fusion Pipeline (Kaggle Execution Script)
# ==========================================================

# Exact verified Kaggle mount path
DATASET_ROOT = "/kaggle/input/datasets/marcesalas/fusion-dataset-59-malware-families-in-png-format/all_malware"
NUM_CLASSES = 59 

# ==========================================================
# PyTorch Dataset Definition
# ==========================================================
class MalwareDataset(Dataset):
    def __init__(self, file_paths, labels, transform=None):
        self.file_paths = file_paths
        self.labels = labels
        self.transform = transform
        
    def __len__(self):
        return len(self.file_paths)
        
    def __getitem__(self, idx):
        # Convert to 3-channel RGB for native ViT patching topology
        img = Image.open(self.file_paths[idx]).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            img = self.transform(img)
            
        return img, label

# ==========================================================
# CutMix & MixUp Augmentations (Anti-Polymorphic Defenses)
# ==========================================================
def rand_bbox(size, lam):
    W = size[2]
    H = size[3]
    cut_rat = np.sqrt(1. - lam)
    cut_w = int(W * cut_rat)
    cut_h = int(H * cut_rat)

    cx = np.random.randint(W)
    cy = np.random.randint(H)

    bbx1 = np.clip(cx - cut_w // 2, 0, W)
    bby1 = np.clip(cy - cut_h // 2, 0, H)
    bbx2 = np.clip(cx + cut_w // 2, 0, W)
    bby2 = np.clip(cy + cut_h // 2, 0, H)

    return bbx1, bby1, bbx2, bby2

def cutmix_data(x, y, alpha=1.0):
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1

    batch_size = x.size()[0]
    index = torch.randperm(batch_size).to(x.device)

    y_a, y_b = y, y[index]
    bbx1, bby1, bbx2, bby2 = rand_bbox(x.size(), lam)
    x[:, :, bbx1:bbx2, bby1:bby2] = x[index, :, bbx1:bbx2, bby1:bby2]
    lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (x.size()[-1] * x.size()[-2]))
    return x, y_a, y_b, lam

def mixup_data(x, y, alpha=1.0):
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1

    batch_size = x.size()[0]
    index = torch.randperm(batch_size).to(x.device)

    mixed_x = lam * x + (1 - lam) * x[index, :]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam

def mixup_criterion(criterion, pred, y_a, y_b, lam):
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)

# ==========================================================
# Main Training & Evaluation Execution
# ==========================================================
def main():
    print("Initializing AegisNet Phase 2 ViT Execution Pipeline...")
    
    # 1. Hardware Initialization & Optimization
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Target Hardware Engine: {device}")
    
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        print("CuDNN Benchmark enabled for optimal GPU throughput.")
        
        gpu_name = torch.cuda.get_device_name(0)
        print(f"Active Accelerator: {gpu_name}")
        if "P100" in gpu_name:
            batch_size = 64
        elif "L4" in gpu_name:
            batch_size = 64
        elif "T4" in gpu_name:
            batch_size = 64
        else:
            batch_size = 32
    else:
        batch_size = 16
        print("WARNING: CPU execution detected. Training will be extremely slow.")
        
    print(f"Allocating System Batch Size: {batch_size}")
    
    # 2. Parse Directory Structure via Dedicated Partitions
    train_files = glob.glob(os.path.join(DATASET_ROOT, "train", "**", "*.png"), recursive=True)
    val_files = glob.glob(os.path.join(DATASET_ROOT, "valid", "**", "*.png"), recursive=True)
    
    if not train_files or not val_files:
        print(f"CRITICAL ERROR: Zero images located at target path: {DATASET_ROOT}")
        return
        
    # Extract structural classes dynamically from train directory
    class_names = sorted(list(set([os.path.basename(os.path.dirname(f)) for f in train_files])))
    class_to_idx = {cls_name: i for i, cls_name in enumerate(class_names)}
    
    train_labels = [class_to_idx[os.path.basename(os.path.dirname(f))] for f in train_files]
    val_labels = [class_to_idx[os.path.basename(os.path.dirname(f))] for f in val_files]
    
    print(f"Dataset Verified: Found {len(train_files)} Training samples and {len(val_files)} Validation samples.")
    print(f"Total Target Output Dimensionality: {len(class_names)} Classes.")
    
    # 3. Advanced Transforms Optimization
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # 4. DataLoaders Matrix Configuration
    train_dataset = MalwareDataset(train_files, train_labels, transform=train_transform)
    val_dataset = MalwareDataset(val_files, val_labels, transform=val_transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)
    
    # 5. Initialize Pre-trained Vision Transformer Backbone
    print("Downloading ImageNet Pre-trained ViT-B/16 Base Topology...")
    model = models.vit_b_16(weights=models.ViT_B_16_Weights.DEFAULT)
    
    # Map final classification layer to the exact malware class count
    model.heads.head = nn.Linear(model.heads.head.in_features, len(class_names))
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    
    num_epochs = 20
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
    
    # Checkpoint Metric Tracking
    best_acc = 0.0
    patience = 5
    epochs_no_improve = 0
    start_epoch = 0
    checkpoint_path = "checkpoint.pt"
    
    # State Engine Checkpoint Recovery
    if os.path.exists(checkpoint_path):
        print("Discovered localized checkpoint state. Synchronizing weights...")
        checkpoint = torch.load(checkpoint_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        start_epoch = checkpoint['epoch'] + 1
        best_acc = checkpoint['best_acc']
        epochs_no_improve = checkpoint['epochs_no_improve']
        print(f"Resuming pipeline execution cleanly from Epoch {start_epoch + 1}")

    # 6. Core Fine-Tuning Execution
    print("\nTraining cycle initialized. Processing features...")
    for epoch in range(start_epoch, num_epochs):
        model.train()
        running_loss = 0.0
        
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            
            # Continuous Regularization MixUp/CutMix Decision
            if np.random.rand(1) < 0.5:
                inputs, targets_a, targets_b, lam = cutmix_data(inputs, targets)
                outputs = model(inputs)
                loss = mixup_criterion(criterion, outputs, targets_a, targets_b, lam)
            else:
                inputs, targets_a, targets_b, lam = mixup_data(inputs, targets)
                outputs = model(inputs)
                loss = mixup_criterion(criterion, outputs, targets_a, targets_b, lam)
                
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)
            
        epoch_loss = running_loss / len(train_dataset)
        scheduler.step()
        
        # Validation Pass
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += targets.size(0)
                correct += (predicted == targets).sum().item()
                
        val_acc = (100.0 * correct) / total
        print(f"Epoch {epoch+1:02d}/{num_epochs} | Loss: {epoch_loss:.4f} | Val Accuracy: {val_acc:.2f}% | LR: {scheduler.get_last_lr()[0]:.6f}")
        
        # Save Transient Checkpoint State
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict(),
            'best_acc': best_acc,
            'epochs_no_improve': epochs_no_improve
        }, checkpoint_path)
        
        # Target Objective Validation Check
        if val_acc > best_acc:
            best_acc = val_acc
            epochs_no_improve = 0
            torch.save(model.state_dict(), "vit_aegisnet_phase2.pt")
            print(f"--> Target Metric Enhanced. Preserved Optimal Weight Signatures ({best_acc:.2f}%)")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Early Stopping Triggered: Convergence stabilized across {patience} consecutive epochs.")
                break
                
    print(f"\nTraining Sequence Complete. Peak Generalization Metric Reached: {best_acc:.2f}%")
    
    # 7. Build Metadata Index Mapping
    mapping = {int(i): str(c) for c, i in class_to_idx.items()}
    with open("vit_label_mapping.json", "w") as f:
        json.dump(mapping, f, indent=4)
    print("Metadata matrix successfully compiled: vit_label_mapping.json")

if __name__ == "__main__":
    main()