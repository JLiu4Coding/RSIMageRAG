"""Image processing utilities for GeoTIFF conversion and analysis."""
import os
from typing import Tuple, Optional, Dict
from pathlib import Path
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

# Optional matplotlib import for classification preview
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None


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


def kmeans_classify_raster(
    image_path: str,
    output_dir: str,
    k: int = 5,
    max_iter: int = 30,
    seed: int = 0,
    save_masks: bool = False
) -> Dict[str, str]:
    """
    Perform K-means classification on a raster image.
    
    Args:
        image_path: Path to input raster (GeoTIFF)
        output_dir: Directory to save output files
        k: Number of classes
        max_iter: Maximum K-means iterations
        seed: Random seed for reproducibility
        save_masks: Whether to save per-class binary masks
        
    Returns:
        Dictionary with paths to output files:
        - classified_tif: Path to classified GeoTIFF
        - preview_png: Path to colored preview PNG
        - masks: List of mask paths (if save_masks=True)
    """
    if not RASTERIO_AVAILABLE:
        raise ImportError("rasterio is required for classification")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Output file paths
    base_name = Path(image_path).stem
    tif_out = os.path.join(output_dir, f"{base_name}_classified_{k}.tif")
    preview_png = os.path.join(output_dir, f"{base_name}_classified_preview_{k}.png")
    
    # Read raster
    with rasterio.open(image_path) as src:
        arr = src.read().astype(np.float32)  # shape: (bands, H, W)
        profile = src.profile
        nodata = src.nodata
    
    bands, H, W = arr.shape
    
    # Build NoData mask
    if nodata is not None:
        nd_mask = np.any(arr == nodata, axis=0)
    else:
        nd_mask = np.zeros(arr.shape[1:], dtype=bool)
    nd_mask |= np.any(~np.isfinite(arr), axis=0)
    
    # Flatten
    X = arr.reshape(bands, -1).T  # (N, bands)
    valid = ~nd_mask.reshape(-1)
    Xv = X[valid]  # valid pixels only
    
    # Standardize features (z-score)
    mean = np.nanmean(Xv, axis=0, dtype=np.float64)
    std = np.nanstd(Xv, axis=0, dtype=np.float64)
    std[std == 0] = 1.0
    Xv_norm = (Xv - mean) / std
    
    # K-Means clustering
    rng = np.random.default_rng(seed)
    N, D = Xv_norm.shape
    
    # Initialize clusters
    idx = rng.choice(N, size=k, replace=False)
    centers = Xv_norm[idx].copy()
    labels = np.full(N, -1, dtype=np.int32)
    
    # K-Means iterations
    for it in range(1, max_iter + 1):
        # Assign pixels to nearest cluster
        x2 = np.sum(Xv_norm * Xv_norm, axis=1, keepdims=True)  # (N,1)
        c2 = np.sum(centers * centers, axis=1)[None, :]  # (1,k)
        dist2 = x2 - 2.0 * (Xv_norm @ centers.T) + c2  # (N,k)
        new_labels = np.argmin(dist2, axis=1)
        
        # Check for convergence
        if labels[0] != -1:
            changed = (new_labels != labels).sum()
            if changed == 0:
                break
        
        labels = new_labels
        
        # Update centers
        for j in range(k):
            mask = (labels == j)
            if np.any(mask):
                centers[j] = Xv_norm[mask].mean(axis=0)
            else:
                # Re-seed empty cluster
                centers[j] = Xv_norm[rng.integers(0, N)]
    
    # Rebuild full label image
    labels_full = np.full(X.shape[0], 255, dtype=np.uint8)  # 255 for invalid
    labels_full[valid] = labels.astype(np.uint8)
    class_map = labels_full.reshape(H, W)
    
    # Save GeoTIFF
    profile_out = profile.copy()
    profile_out.update(dtype=rasterio.uint8, count=1, nodata=255, compress="lzw")
    with rasterio.open(tif_out, "w", **profile_out) as dst:
        dst.write(class_map, 1)
    
    # Save colored preview PNG
    if MATPLOTLIB_AVAILABLE:
        plt.figure(figsize=(10, 8))
        plt.imshow(class_map, cmap="tab10", interpolation="nearest")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(preview_png, dpi=200, bbox_inches='tight')
        plt.close()
    else:
        # Fallback: convert to PIL image
        preview_img = Image.fromarray(class_map, mode='L')
        preview_img = preview_img.convert('RGB')
        preview_img.save(preview_png)
    
    result = {
        "classified_tif": tif_out,
        "preview_png": preview_png
    }
    
    # Optional: per-class binary masks
    if save_masks:
        mask_paths = []
        for i in range(k):
            mask_img = (class_map == i).astype(np.uint8) * 255
            mask_path = os.path.join(output_dir, f"{base_name}_class_{i}.png")
            Image.fromarray(mask_img).save(mask_path)
            mask_paths.append(mask_path)
        result["masks"] = mask_paths
    
    return result

