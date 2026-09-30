import torch
import torch.nn.functional as F

def masked_mse_loss(pred, target, mask):
    """
    Computes MSE only where mask == 1.
    mask: boolean or float tensor identical in spatial shape to target.
    """
    error = (pred - target) ** 2
    
    # Expand mask if necessary to match channels implicitly
    if mask.dim() < error.dim():
        mask = mask.unsqueeze(1).expand_as(error)
        
    masked_error = error * mask
    
    # Avoid zero division
    valid_count = torch.clamp(mask.sum(), min=1e-6)
    
    return masked_error.sum() / valid_count

class OceanEmbedTrainer:
    def __init__(self, model, train_loader, val_loader, device='cuda', lr=1e-3, epochs=50):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.epochs = epochs
        self.early_stop_patience = 8
        self.epochs_no_improve = 0
        
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-4)
        
        # SIH Prototype uses mixed precision for optimal speed on RTX 3060
        self.scaler = torch.amp.GradScaler('cuda')
        self.history = []
        
        # Simple StepLR
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='min', patience=3, factor=0.5)

    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        
        for batch_idx, batch in enumerate(self.train_loader):
            X = batch['X'].to(self.device)         # [B, 49, H, W]
            Y = batch['Y'].to(self.device)         # [B, 15, H, W]
            Y_mask = batch['Y_mask'].to(self.device) # [B, H, W] or [B, 15, H, W]
            
            self.optimizer.zero_grad(set_to_none=True)
            
            with torch.amp.autocast('cuda'):
                pred = self.model(X)
                loss = masked_mse_loss(pred, Y, Y_mask)
            
            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()
            
            total_loss += loss.item()
            
        return total_loss / max(1, len(self.train_loader))

    def validate(self):
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch in self.val_loader:
                X = batch['X'].to(self.device)
                Y = batch['Y'].to(self.device)
                Y_mask = batch['Y_mask'].to(self.device)
                
                with torch.amp.autocast('cuda'):
                    pred = self.model(X)
                    loss = masked_mse_loss(pred, Y, Y_mask)
                    
                total_loss += loss.item()
                
        return total_loss / max(1, len(self.val_loader))

    def fit(self, save_path="checkpoints/tc_resunet_best.pt"):
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        best_val_loss = float('inf')
        
        for epoch in range(1, self.epochs + 1):
            train_loss = self.train_epoch(epoch)
            val_loss = self.validate()
            
            current_lr = self.optimizer.param_groups[0]['lr']
            print(f"Epoch {epoch:03d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | LR: {current_lr:.2e}")
            
            self.scheduler.step(val_loss)
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.epochs_no_improve = 0
                torch.save(self.model.state_dict(), save_path)
                print(f"  -> Saved Best Model (Val Loss: {best_val_loss:.4f})")
            else:
                self.epochs_no_improve += 1
                
            # Latest checkpoints enforcing iteration constraints
            torch.save(self.model.state_dict(), os.path.join(os.path.dirname(save_path), "latest_model.pt"))
            self.history.append({'epoch': epoch, 'train_loss': train_loss, 'val_loss': val_loss})
            import pandas as pd
            pd.DataFrame(self.history).to_csv(os.path.join(os.path.dirname(save_path), "training_history.csv"), index=False)
            
            if self.epochs_no_improve >= self.early_stop_patience:
                print(f"Early Stopping Trigggered! Validation natively ceased descending after {self.early_stop_patience} sweeps cleanly.")
                break
                
        return best_val_loss
