"""RAG service for question answering using image captions."""
from typing import List, Dict
from langchain_openai import ChatOpenAI
from app.services.image_service import ImageService
from app.config import settings


class RAGService:
    """Service for RAG-based question answering."""
    
    def __init__(self, image_service: ImageService):
        """
        Initialize RAG service.
        
        Args:
            image_service: Image service instance
        """
        self.image_service = image_service
        self.llm = ChatOpenAI(model=settings.vision_model)
    
    def answer_question(self, question: str, k: int = 4) -> Dict:
        """
        Answer question using RAG with image captions.
        
        Args:
            question: User question
            k: Number of relevant images to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve relevant images
        results = self.image_service.search_images(question, k=k)
        
        # Build context from retrieved images
        context_parts = []
        for i, result in enumerate(results, 1):
            snippet = result.get("snippet", "")
            context_parts.append(f"Image {i}:\n{snippet}\n")
        
        context = "\n".join(context_parts)
        
        # Generate answer using LLM
        prompt = f"""You are a remote sensing analyst assistant. Answer the question based on the provided image analysis context.

Context from images:
{context}

Question: {question}

Provide a clear, concise answer based on the context. If the context doesn't contain enough information, say so."""
        
        response = self.llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        return {
            "answer": answer,
            "sources": results
        }

