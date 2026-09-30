import xarray as xr
import numpy as np

class MonthlyClimatologyBaseline:
    def __init__(self):
        self.climatology_mean = None
        self.depths = None
        
    def fit(self, train_Y_xr):
        """
        train_Y_xr: xarray DataArray of shape (T, Depths, Lat, Lon)
        Calculates historical mean temperature at each (month, depth, lat, lon).
        """
        print(f"Fitting Climatology onto Training Set strictly... ({len(train_Y_xr.time)} time steps)")
        
        # Group by month and calculate the mean natively across exactly the training bounds
        self.climatology_mean = train_Y_xr.groupby('time.month').mean(dim='time')
        self.depths = train_Y_xr.depth.values
        
        print(f"Climatology constructed. Months mapped: {self.climatology_mean.month.values}")
        
    def predict(self, target_Y_xr):
        """
        target_Y_xr: xarray DataArray (T, Depths, Lat, Lon) used purely to extract
                     target timestamps to generate the climatology map array.
        Returns a numpy array identical in shape to target_Y_xr
        """
        if self.climatology_mean is None:
            raise ValueError("Climatology must be fitted before prediction.")
            
        predictions = []
        months = target_Y_xr['time.month'].values
        
        # We can map rapidly by fetching the spatial slice for each time step's index natively
        for m in months:
            # self.climatology_mean has shape (month=12, depth=15, lat=101, lon=241)
            pred_slice = self.climatology_mean.sel(month=m, method='nearest').values
            predictions.append(pred_slice)
            
        return np.stack(predictions, axis=0)
