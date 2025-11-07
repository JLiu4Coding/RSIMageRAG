# Installation Guide

## Python 3.13 Compatibility Notes

If you encounter issues installing `rasterio` on Windows with Python 3.13, try one of these solutions:

### Option 1: Install rasterio separately (Recommended)
```bash
# First install numpy
pip install numpy>=1.26.4

# Then try installing rasterio (it will use available wheels)
pip install rasterio

# If that fails, install from conda-forge
conda install -c conda-forge rasterio
```

### Option 2: Use Python 3.11 or 3.12
Rasterio has better pre-built wheel support for Python 3.11 and 3.12:
```bash
# Create a new environment with Python 3.12
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Option 3: Install GDAL first (Windows)
On Windows, you may need to install GDAL dependencies first:
1. Download GDAL from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
2. Install the appropriate wheel for your Python version
3. Then install rasterio

### Option 4: Skip rasterio (if not using GeoTIFF features)
If you're not using GeoTIFF centroid extraction, you can comment out rasterio in requirements.txt and modify the code to handle missing rasterio gracefully.

## Standard Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# If rasterio fails, install it separately (see options above)
pip install rasterio
```

## Troubleshooting

- **rasterio build errors**: Use conda or install pre-built wheels
- **numpy version conflicts**: Ensure numpy is installed before rasterio
- **GDAL errors**: Install GDAL system libraries first

