import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.tc_resunet import TCResUNet
from src.training.trainer import OceanEmbedTrainer
from src.data.dataset import OceanEmbedDataset
import xarray as xr
from torch.utils.data import DataLoader
import torch

def main():
    DATA_DIR = "data/processed"
    
    print("Loading Processed NetCDF Splits...")
    try:
        X_train = xr.open_dataset(os.path.join(DATA_DIR, "X_train.nc"))
        Y_train = xr.open_dataset(os.path.join(DATA_DIR, "Y_train.nc"))
        X_val = xr.open_dataset(os.path.join(DATA_DIR, "X_val.nc"))
        Y_val = xr.open_dataset(os.path.join(DATA_DIR, "Y_val.nc"))
    except Exception as e:
        print(f"Error loading datasets. Did 05_prepare_training_data run successfully? {e}")
        return

    # Window size 7 explicitly defined for sequential lags natively
    bs = 8
    
    print("Initializing PyTorch Datasets (Window=7)...")
    train_dataset = OceanEmbedDataset(X_train['__xarray_dataarray_variable__'] if '__xarray_dataarray_variable__' in X_train else X_train, 
                                      Y_train['thetao'] if 'thetao' in Y_train else Y_train, window_size=7)
    val_dataset = OceanEmbedDataset(X_val['__xarray_dataarray_variable__'] if '__xarray_dataarray_variable__' in X_val else X_val, 
                                    Y_val['thetao'] if 'thetao' in Y_val else Y_val, window_size=7)
    
    train_loader = DataLoader(train_dataset, batch_size=bs, shuffle=True, pin_memory=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=bs, shuffle=False, pin_memory=True, num_workers=2)

    print(f"Train batches: {len(train_loader)} | Val batches: {len(val_loader)}")

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Instantiating TC-ResUNet on {device}...")
    
    # 7 variables * 7 window elements = 49 input channels
    model = TCResUNet(in_channels=49, out_channels=15, base_c=32)
    
    # Train bounded cleanly scaling exactly via PyTorch Early Stopping triggering natively locally
    trainer = OceanEmbedTrainer(model, train_loader, val_loader, device=device, lr=1e-3, epochs=100)
    
    print("Executing Training Phase...")
    best_loss = trainer.fit(save_path="checkpoints/tc_resunet_best.pt")
    print(f"\\nTraining complete! Best Validation Loss: {best_loss:.4f}")
    
if __name__ == "__main__":
    main()
