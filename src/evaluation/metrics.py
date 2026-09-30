import numpy as np

def calculate_depthwise_metrics(pred, target, mask):
    """
    pred, target: (T, Depths, H, W) arrays natively from Inference.
    mask: valid domain boolean (H, W).
    Returns depth-indexed metrics dictionary evaluating Bias, MAE, RMSE natively.
    """
    # Assuming depths are index 1 (second dimension)
    num_depths = pred.shape[1]
    
    metrics = {
        'rmse': np.zeros(num_depths),
        'mae': np.zeros(num_depths),
        'bias': np.zeros(num_depths),
        'corr': np.zeros(num_depths)
    }
    
    # Broadcast mask statically across frames
    for d in range(num_depths):
        p_d = pred[:, d, :, :]
        t_d = target[:, d, :, :]
        
        # Valid elements exclusively evaluating bathymetry bounds natively
        # since landmask is completely static across time limits!
        valid = ~np.isnan(t_d[0])
        
        # Flatten natively mapped points
        p_valid = p_d[:, valid].flatten()
        t_valid = t_d[:, valid].flatten()
        
        error = p_valid - t_valid
        
        metrics['bias'][d] = np.mean(error)
        metrics['mae'][d] = np.mean(np.abs(error))
        metrics['rmse'][d] = np.sqrt(np.mean(error**2))
        
        # Pearson correlation (avoid division by 0)
        std_p = np.std(p_valid)
        std_t = np.std(t_valid)
        if std_p > 0 and std_t > 0:
            cov = np.cov(p_valid, t_valid)[0, 1]
            metrics['corr'][d] = cov / (std_p * std_t)
        else:
            metrics['corr'][d] = np.nan
            
    return metrics
