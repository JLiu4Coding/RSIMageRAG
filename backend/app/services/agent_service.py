"""Agent service for autonomous image analysis."""
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from app.services.image_service import ImageService
from app.config import settings


# Global image_service reference for tools
image_service: Optional[ImageService] = None


@tool
def analyze_image_tool(image_id: str) -> str:
    """
    Analyze a specific image using vision model.
    
    Args:
        image_id: Image identifier
        
    Returns:
        Analysis results as string
    """
    global image_service
    if image_service is None:
        return "Error: Image service not initialized"
    
    try:
        result = image_service.analyze_image(image_id)
        return f"Analysis complete: {result.get('summary', 'No summary available')}"
    except Exception as e:
        return f"Error analyzing image: {str(e)}"


@tool
def search_images_tool(query: str, k: int = 4) -> str:
    """
    Search for images by natural language query.
    
    Args:
        query: Search query
        k: Number of results
        
    Returns:
        Search results as string
    """
    global image_service
    if image_service is None:
        return "Error: Image service not initialized"
    
    try:
        results = image_service.search_images(query, k=k)
        if not results:
            return "No images found matching the query."
        return f"Found {len(results)} images: {', '.join([r.get('jpeg_path', 'unknown') for r in results])}"
    except Exception as e:
        return f"Error searching images: {str(e)}"


class AgentService:
    """Service for agentic analysis with tools."""
    
    def __init__(self, image_service: ImageService):
        """
        Initialize agent service.
        
        Args:
            image_service: Image service instance
        """
        self.image_service = image_service
        self.llm = ChatOpenAI(
            model=settings.vision_model,
            temperature=0
        )
        self.tools = [analyze_image_tool, search_images_tool]
        # Bind tools to LLM
        self.agent = self.llm.bind_tools(self.tools)
        
        # Set global reference for tools
        set_image_service(image_service)
    
    def process_query(self, query: str, image_id: Optional[str] = None) -> Dict:
        """
        Process query using agent with tools.
        
        Note: This is a simplified implementation. For full agentic behavior
        with tool execution, you may need to implement a proper agent loop
        that handles tool calls and responses iteratively.
        
        Args:
            query: User query
            image_id: Optional specific image to analyze
            
        Returns:
            Dictionary with result, steps, and tools used
        """
        steps = []
        tools_used = []
        
        # If image_id provided, analyze it first
        if image_id:
            steps.append(f"Analyzing image {image_id}")
            try:
                analysis = self.image_service.analyze_image(image_id)
                steps.append(f"Analysis complete: {analysis.get('summary', '')}")
                tools_used.append("analyze_image_tool")
            except Exception as e:
                steps.append(f"Error: {str(e)}")
        
        # Use agent to process query
        try:
            response = self.agent.invoke(query)
            steps.append(f"Agent response: {response.content}")
            
            # Check if agent wants to use tools
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get('name', 'unknown')
                    tools_used.append(tool_name)
                    steps.append(f"Tool called: {tool_name}")
            
            result = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            result = f"Error processing query: {str(e)}"
            steps.append(f"Error: {str(e)}")
        
        return {
            "result": result,
            "steps": steps,
            "tools_used": list(set(tools_used))
        }


def set_image_service(service: ImageService) -> None:
    """Set global image service for tools."""
    global image_service
    image_service = service
