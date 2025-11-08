"""Main FastAPI application."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List
import os
import uuid
from pathlib import Path

from app.config import settings
from app.models.schemas import (
    ImageUploadResponse,
    MultipleImageUploadResponse,
    ImageUploadItem,
    ImageAnalysisRequest,
    ImageAnalysisResponse,
    QueryRequest,
    QueryResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    AgentQueryRequest,
    AgentQueryResponse
)
from app.services.image_service import ImageService
from app.services.rag_service import RAGService
from app.services.agent_service import AgentService, set_image_service

# Set environment variables for boto3 (as backup)
os.environ.setdefault("AWS_ACCESS_KEY_ID", settings.aws_access_key_id)
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", settings.aws_secret_access_key)
os.environ.setdefault("AWS_DEFAULT_REGION", settings.aws_default_region)
os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)

# Initialize FastAPI app
app = FastAPI(title="ImageRAG API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
image_service = ImageService()
rag_service = RAGService(image_service)
agent_service = AgentService(image_service)
set_image_service(image_service)  # For agent tools


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "ImageRAG API", "version": "1.0.0"}


@app.post("/api/images/upload", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a single image file to S3.
    
    Args:
        file: Image file to upload
        
    Returns:
        Image upload response with image_id and S3 URL
    """
    try:
        # Save uploaded file to permanent location for analysis
        image_service.upload_dir.mkdir(exist_ok=True)
        file_ext = Path(file.filename).suffix
        temp_filename = f"{uuid.uuid4()}{file_ext}"
        local_path = image_service.upload_dir / temp_filename
        
        # Write file content
        content = await file.read()
        with open(local_path, "wb") as f:
            f.write(content)
        
        # Upload to S3 (this will also save a copy locally for analysis)
        image_id, s3_url = image_service.upload_image(str(local_path), file.filename)
        
        return ImageUploadResponse(
            image_id=image_id,
            s3_url=s3_url,
            message="Image uploaded successfully"
        )
    except Exception as e:
        # Clean up on error
        if 'local_path' in locals() and local_path.exists():
            os.unlink(local_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/images/upload-multiple", response_model=MultipleImageUploadResponse)
async def upload_multiple_images(files: List[UploadFile] = File(..., description="Multiple image files")):
    """
    Upload multiple image files to S3.
    
    Args:
        files: List of image files to upload
        
    Returns:
        Multiple image upload response with success and failure lists
    """
    uploaded = []
    failed = []
    
    for file in files:
        local_path = None
        try:
            # Save uploaded file to permanent location for analysis
            image_service.upload_dir.mkdir(exist_ok=True)
            file_ext = Path(file.filename).suffix
            temp_filename = f"{uuid.uuid4()}{file_ext}"
            local_path = image_service.upload_dir / temp_filename
            
            # Write file content
            content = await file.read()
            with open(local_path, "wb") as f:
                f.write(content)
            
            # Upload to S3
            image_id, s3_url = image_service.upload_image(str(local_path), file.filename)
            
            uploaded.append(ImageUploadItem(
                image_id=image_id,
                filename=file.filename,
                s3_url=s3_url
            ))
        except Exception as e:
            # Clean up on error
            if local_path and local_path.exists():
                os.unlink(local_path)
            failed.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return MultipleImageUploadResponse(
        uploaded=uploaded,
        failed=failed,
        total=len(files),
        success_count=len(uploaded),
        failed_count=len(failed)
    )


@app.post("/api/images/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analyze uploaded image using vision model.
    
    Args:
        request: Image analysis request
        
    Returns:
        Image analysis response
    """
    try:
        result = image_service.analyze_image(request.image_id)
        return ImageAnalysisResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/images/search", response_model=QueryResponse)
async def search_images(request: QueryRequest):
    """
    Search for images using natural language query.
    
    Args:
        request: Search query request
        
    Returns:
        Query response with matching images
    """
    try:
        results = image_service.search_images(request.query, request.k)
        return QueryResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rag/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """
    Answer question using RAG with image captions.
    
    Args:
        request: RAG query request
        
    Returns:
        RAG query response with answer and sources
    """
    try:
        result = rag_service.answer_question(request.question, request.k)
        return RAGQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/query", response_model=AgentQueryResponse)
async def agent_query(request: AgentQueryRequest):
    """
    Process query using agentic analysis with tools.
    
    Args:
        request: Agent query request
        
    Returns:
        Agent query response with result and steps
    """
    try:
        result = agent_service.process_query(request.query, request.image_id)
        return AgentQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/images/{image_id}/url")
async def get_image_url(image_id: str):
    """
    Get presigned URL for image.
    
    Args:
        image_id: Image identifier
        
    Returns:
        Presigned S3 URL
    """
    url = image_service.get_image_url(image_id)
    if not url:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"image_id": image_id, "url": url}


@app.get("/api/images/{image_id}/file")
async def get_image_file(image_id: str):
    """
    Serve image file directly from backend (always returns JPEG for display).
    
    Args:
        image_id: Image identifier
        
    Returns:
        Image file (JPEG format for browser compatibility)
    """
    if image_id not in image_service._image_metadata:
        raise HTTPException(status_code=404, detail="Image not found")
    
    metadata = image_service._image_metadata[image_id]
    
    # Prefer JPEG version if available
    jpeg_path = metadata.get("jpeg_path")
    if jpeg_path and os.path.exists(jpeg_path):
        return FileResponse(
            jpeg_path,
            media_type="image/jpeg",
            filename=f"{Path(metadata.get('filename', 'image')).stem}.jpg"
        )
    
    # Fallback to original file, but convert to JPEG on-the-fly if TIFF
    local_path = metadata.get("local_path")
    if not local_path or not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    ext = Path(local_path).suffix.lower()
    if ext in [".tif", ".tiff"]:
        # Convert TIFF to JPEG on-the-fly
        try:
            from app.utils.image_processing import convert_geotiff_to_jpeg
            jpeg_path = convert_geotiff_to_jpeg(local_path, str(image_service.jpeg_dir))
            # Update metadata for future requests
            metadata["jpeg_path"] = jpeg_path
            return FileResponse(
                jpeg_path,
                media_type="image/jpeg",
                filename=f"{Path(metadata.get('filename', 'image')).stem}.jpg"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to convert TIFF to JPEG: {str(e)}")
    else:
        # Already JPEG or other supported format
        media_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
        return FileResponse(
            local_path,
            media_type=media_type,
            filename=metadata.get("filename", "image")
        )


if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path
    
    # Ensure we're in the backend directory and add it to path
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

