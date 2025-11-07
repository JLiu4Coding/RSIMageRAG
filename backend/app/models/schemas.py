"""Pydantic schemas for API requests and responses."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    """Response for image upload."""
    image_id: str
    s3_url: str
    message: str


class ImageAnalysisRequest(BaseModel):
    """Request for image analysis."""
    image_id: str


class ImageAnalysisResponse(BaseModel):
    """Response for image analysis."""
    image_id: str
    location_guess: Optional[str] = None
    land_cover: Optional[str] = None
    urban_structure: Optional[str] = None
    notable_features: Optional[str] = None
    summary: Optional[str] = None
    raw_analysis: Dict[str, Any]


class QueryRequest(BaseModel):
    """Request for image retrieval query."""
    query: str
    k: int = 4


class QueryResponse(BaseModel):
    """Response for image retrieval query."""
    results: List[Dict[str, Any]]


class RAGQueryRequest(BaseModel):
    """Request for RAG-based question answering."""
    question: str
    k: int = 4


class RAGQueryResponse(BaseModel):
    """Response for RAG-based question answering."""
    answer: str
    sources: List[Dict[str, Any]]


class AgentQueryRequest(BaseModel):
    """Request for agentic analysis."""
    query: str
    image_id: Optional[str] = None


class AgentQueryResponse(BaseModel):
    """Response for agentic analysis."""
    result: str
    steps: List[str]
    tools_used: List[str]

