"""Vector store management for image captions."""
import os
import json
from typing import Dict, List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class VectorStoreManager:
    """Manages FAISS vector store for image caption retrieval."""
    
    def __init__(self, embedding_model: str = "text-embedding-3-small", persist_dir: str = "vectorstore"):
        """
        Initialize vector store manager.
        
        Args:
            embedding_model: OpenAI embedding model name
            persist_dir: Directory to persist vector store
        """
        self.embedding_model = embedding_model
        self.persist_dir = persist_dir
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.vectorstore: Optional[FAISS] = None
        self._load_or_create()
    
    def _load_or_create(self) -> None:
        """Load existing vector store or create new one."""
        if os.path.exists(self.persist_dir) and os.path.isdir(self.persist_dir):
            try:
                # Check if vectorstore files exist
                index_file = os.path.join(self.persist_dir, "index.faiss")
                if os.path.exists(index_file):
                    self.vectorstore = FAISS.load_local(
                        self.persist_dir,
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    return
            except Exception:
                pass
        
        # Initialize as None - will be created lazily on first add
        self.vectorstore = None
    
    def _ensure_vectorstore(self) -> None:
        """Ensure vectorstore is initialized, create if needed."""
        if self.vectorstore is None:
            # Create with a dummy entry first to initialize the index
            self.vectorstore = FAISS.from_texts(
                ["initialization placeholder"],
                self.embeddings,
                metadatas=[{"_placeholder": True}]
            )
    
    def add_image_analysis(
        self,
        jpeg_path: str,
        geotiff_path: str,
        lat: Optional[float],
        lon: Optional[float],
        location_context: str,
        llm_info: Dict
    ) -> None:
        """
        Add image analysis to vector store.
        
        Args:
            jpeg_path: Path to JPEG file
            geotiff_path: Path to original GeoTIFF
            lat: Latitude
            lon: Longitude
            location_context: Location context string
            llm_info: LLM analysis results
        """
        self._ensure_vectorstore()
        
        combined_text = (
            f"jpeg: {os.path.basename(jpeg_path)}\n"
            f"geotiff: {os.path.basename(geotiff_path) if geotiff_path else ''}\n"
            f"path: {geotiff_path}\n"
            f"{location_context}\n\n"
            f"LLM:\n{json.dumps(llm_info, ensure_ascii=False)}"
        )
        
        metadata = {
            "jpeg_path": jpeg_path,
            "geotiff_path": geotiff_path,
            "lat": lat,
            "lon": lon
        }
        
        doc = Document(page_content=combined_text, metadata=metadata)
        self.vectorstore.add_documents([doc])
        self._save()
    
    def search(self, query: str, k: int = 4) -> List[Dict]:
        """
        Search for similar images by query.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of result dictionaries
        """
        if self.vectorstore is None:
            return []
        
        try:
            docs = self.vectorstore.similarity_search(query, k=k)
            # Filter out placeholder entries
            results = []
            for d in docs:
                if not d.metadata.get("_placeholder", False):
                    results.append({
                        "jpeg_path": d.metadata.get("jpeg_path"),
                        "geotiff_path": d.metadata.get("geotiff_path"),
                        "lat": d.metadata.get("lat"),
                        "lon": d.metadata.get("lon"),
                        "snippet": d.page_content[:300] + "..." if d.page_content else None
                    })
            return results
        except Exception:
            return []
    
    def _save(self) -> None:
        """Save vector store to disk."""
        if self.vectorstore:
            os.makedirs(self.persist_dir, exist_ok=True)
            self.vectorstore.save_local(self.persist_dir)

