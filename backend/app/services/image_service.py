"""Image service for managing image uploads and analysis."""
import os
import uuid
from typing import Dict, Optional, Tuple, List
from pathlib import Path
from app.config import settings
from app.utils.image_processing import geotiff_centroid_wgs84, convert_geotiff_to_jpeg
from app.utils.s3_client import S3Client
from app.utils.llm_analysis import analyze_image_with_llm
from app.utils.vectorstore import VectorStoreManager
from langchain_openai import ChatOpenAI


class ImageService:
    """Service for image operations."""
    
    def __init__(self):
        """Initialize image service."""
        self.s3_client = S3Client(
            settings.aws_s3_bucket,
            settings.aws_default_region,
            access_key_id=settings.aws_access_key_id,
            secret_access_key=settings.aws_secret_access_key
        )
        self.vectorstore = VectorStoreManager(
            settings.embedding_model,
            settings.vectorstore_dir
        )
        self.llm = ChatOpenAI(model=settings.vision_model)
        self.upload_dir = Path(settings.upload_dir)
        self.jpeg_dir = Path(settings.jpeg_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.jpeg_dir.mkdir(exist_ok=True)
        self._image_metadata: Dict[str, Dict] = {}
    
    def upload_image(self, file_path: str, filename: str) -> Tuple[str, str]:
        """
        Upload image to S3 and return metadata.
        
        Args:
            file_path: Local file path
            filename: Original filename
            
        Returns:
            Tuple of (image_id, s3_url)
        """
        image_id = str(uuid.uuid4())
        s3_key = f"images/{image_id}/{filename}"
        
        # Determine content type
        ext = Path(filename).suffix.lower()
        content_type = "image/tiff" if ext in [".tif", ".tiff"] else "image/jpeg"
        
        # Convert to JPEG if TIFF (for frontend display)
        jpeg_path = None
        ext = Path(filename).suffix.lower()
        if ext in [".tif", ".tiff"]:
            try:
                jpeg_path = convert_geotiff_to_jpeg(file_path, str(self.jpeg_dir))
                # Also upload JPEG version to S3
                jpeg_s3_key = f"images/{image_id}/{Path(filename).stem}.jpg"
                jpeg_content_type = "image/jpeg"
                self.s3_client.upload_file(jpeg_path, jpeg_s3_key, jpeg_content_type)
                # Use JPEG for display URL
                s3_key_for_url = jpeg_s3_key
            except Exception as e:
                print(f"Warning: Failed to convert TIFF to JPEG: {e}")
                jpeg_path = None
                s3_key_for_url = s3_key
        else:
            s3_key_for_url = s3_key
        
        # Upload original to S3
        upload_success = self.s3_client.upload_file(file_path, s3_key, content_type)
        if not upload_success:
            raise Exception("Failed to upload image to S3")
        
        # Generate presigned URL (prefer JPEG if available)
        s3_url = self.s3_client.generate_presigned_url(s3_key_for_url, expires_in=86400)
        
        # Fallback: use backend URL if S3 URL generation fails
        if not s3_url:
            print(f"Warning: S3 presigned URL generation failed for {s3_key_for_url}, using backend URL")
            s3_url = f"/api/images/{image_id}/file"
        
        # Store metadata
        self._image_metadata[image_id] = {
            "filename": filename,
            "s3_key": s3_key,
            "local_path": file_path,
            "jpeg_path": jpeg_path,  # Store JPEG path for serving
            "s3_url": s3_url
        }
        
        return image_id, s3_url
    
    def analyze_image(self, image_id: str) -> Dict:
        """
        Analyze image using vision model.
        
        Args:
            image_id: Image identifier
            
        Returns:
            Analysis results dictionary
        """
        if image_id not in self._image_metadata:
            raise ValueError(f"Image {image_id} not found")
        
        metadata = self._image_metadata[image_id]
        local_path = metadata["local_path"]
        
        # Check if file exists
        if not os.path.exists(local_path):
            raise FileNotFoundError(
                f"Image file not found at {local_path}. "
                "The file may have been deleted or moved."
            )
        
        # Extract centroid if GeoTIFF
        lat, lon = geotiff_centroid_wgs84(local_path)
        location_context = (
            f"Centroid (WGS84): {lat:.6f}, {lon:.6f}"
            if (lat is not None and lon is not None)
            else "Centroid unknown (no CRS)."
        )
        
        # Convert to JPEG if not already converted during upload
        jpeg_path = metadata.get("jpeg_path")
        if not jpeg_path or not os.path.exists(jpeg_path):
            jpeg_path = convert_geotiff_to_jpeg(local_path, str(self.jpeg_dir))
            metadata["jpeg_path"] = jpeg_path
        
        # Analyze with LLM
        llm_info = analyze_image_with_llm(self.llm, jpeg_path, location_context)
        
        # Add to vector store
        self.vectorstore.add_image_analysis(
            jpeg_path,
            local_path,
            lat,
            lon,
            location_context,
            llm_info
        )
        
        # Update metadata
        metadata["analysis"] = llm_info
        metadata["jpeg_path"] = jpeg_path
        metadata["lat"] = lat
        metadata["lon"] = lon
        
        return {
            "image_id": image_id,
            **llm_info,
            "raw_analysis": llm_info
        }
    
    def search_images(self, query: str, k: int = 4) -> List[Dict]:
        """
        Search for images by natural language query.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of matching image results
        """
        results = self.vectorstore.search(query, k=k)
        
        # Enrich with S3 URLs
        for result in results:
            jpeg_path = result.get("jpeg_path")
            if jpeg_path:
                # Find image_id from jpeg_path or metadata
                for img_id, meta in self._image_metadata.items():
                    if meta.get("jpeg_path") == jpeg_path:
                        result["image_id"] = img_id
                        result["s3_url"] = meta.get("s3_url", "")
                        break
        
        return results
    
    def get_image_url(self, image_id: str) -> Optional[str]:
        """
        Get presigned URL for image.
        
        Args:
            image_id: Image identifier
            
        Returns:
            Presigned S3 URL or None
        """
        if image_id in self._image_metadata:
            s3_key = self._image_metadata[image_id]["s3_key"]
            return self.s3_client.generate_presigned_url(s3_key, expires_in=3600)
        return None

