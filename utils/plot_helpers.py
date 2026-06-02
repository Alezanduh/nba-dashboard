# utils/plot_helpers.py
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

def get_smooth_xy(x_series, y_series, points=1000):
    """Generic Pchip smoother for any game-time series data."""
    # Drop duplicates and keep the max value for that second
    clean = pd.DataFrame({'x': x_series, 'y': y_series}).groupby('x')['y'].max().reset_index()
    
    if len(clean) < 2: # Edge case for short quarters
        return x_series, y_series
        
    pchip = PchipInterpolator(clean['x'], clean['y'])
    x_smooth = np.linspace(x_series.min(), x_series.max(), points)
    return x_smooth, pchip(x_smooth)

def apply_custom_grid(ax, y_step, is_marginal=False):
    """Standardized grid styling for the dashboard."""
    ymin, ymax = ax.get_ylim()
    start = y_step * np.floor(ymin / y_step)
    end = y_step * np.ceil(ymax / y_step)
    
    for y in np.arange(start, end + y_step, y_step):
        if not (is_marginal and y == 0):
            ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.8, alpha=0.4, zorder=0)