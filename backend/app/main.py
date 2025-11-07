"""Main FastAPI application."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from pathlib import Path

from app.config import settings
from app.models.schemas import (
    ImageUploadResponse,
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
    Upload image file to S3.
    
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

