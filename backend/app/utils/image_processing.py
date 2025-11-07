"""Image processing utilities for GeoTIFF conversion and analysis."""
import os
from typing import Tuple, Optional
import numpy as np
from PIL import Image

# Optional rasterio import - app can run without it
try:
    import rasterio
    from rasterio.warp import transform as rio_transform
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    rasterio = None
    rio_transform = None


def geotiff_centroid_wgs84(tif_path: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract centroid coordinates from GeoTIFF in WGS84.
    
    Args:
        tif_path: Path to GeoTIFF file
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if no CRS or rasterio unavailable
    """
    if not RASTERIO_AVAILABLE:
        return None, None
    
    try:
        with rasterio.open(tif_path) as src:
            b = src.bounds
            cx = (b.left + b.right) / 2.0
            cy = (b.bottom + b.top) / 2.0
            if src.crs is None:
                return None, None
            if str(src.crs).lower() in ("epsg:4326", "wgs84", "ogc:crs84"):
                lon, lat = cx, cy
            else:
                lon, lat = rio_transform(src.crs, "EPSG:4326", [cx], [cy])
                lon, lat = float(lon[0]), float(lat[0])
        return lat, lon
    except Exception:
        return None, None


def _percentile_stretch(band: np.ndarray, lo: int = 2, hi: int = 98) -> np.ndarray:
    """Apply percentile stretch to normalize band values."""
    lo_v, hi_v = np.nanpercentile(band, lo), np.nanpercentile(band, hi)
    span = max(hi_v - lo_v, 1e-6)
    arr = np.clip((band - lo_v) / span, 0, 1)
    return (arr * 255).astype("uint8")


def convert_geotiff_to_jpeg(tif_path: str, out_dir: str) -> str:
    """
    Convert GeoTIFF to JPEG format for vision API.
    
    Args:
        tif_path: Path to input GeoTIFF
        out_dir: Output directory for JPEG
        
    Returns:
        Path to created JPEG file
    """
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(tif_path))[0]
    out_path = os.path.join(out_dir, base + ".jpg")

    # Try PIL path first
    try:
        im = Image.open(tif_path).convert("RGB")
        im.thumbnail((2048, 2048))
        im.save(out_path, "JPEG", quality=85, optimize=True)
        return out_path
    except Exception:
        pass  # fallback to rasterio

    # Rasterio fallback for multi-band processing
    if not RASTERIO_AVAILABLE:
        raise Exception("rasterio not available - cannot process multi-band GeoTIFF")
    
    with rasterio.open(tif_path) as src:
        bands = list(range(1, min(3, src.count) + 1))
        if len(bands) >= 3:
            arr = src.read(bands).astype("float32")
            rgb = np.stack([_percentile_stretch(arr[i]) for i in range(3)], axis=-1)
        else:
            b1 = src.read(1).astype("float32")
            b = _percentile_stretch(b1)
            rgb = np.stack([b, b, b], axis=-1)

    im = Image.fromarray(rgb)
    im.thumbnail((2048, 2048))
    im.save(out_path, "JPEG", quality=85, optimize=True)
    return out_path

