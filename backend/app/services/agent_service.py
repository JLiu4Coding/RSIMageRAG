"""Agent service for autonomous image analysis."""
import os
from typing import List, Dict, Optional
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from app.services.image_service import ImageService
from app.config import settings
from app.utils.image_processing import kmeans_classify_raster, RASTERIO_AVAILABLE


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


@tool
def classify_image_tool(image_id: str, k: int = 5, max_iter: int = 30, seed: int = 0) -> str:
    """
    Perform K-means classification on a raster image.
    
    This tool performs unsupervised classification using K-means clustering
    on the pixel values of a raster image. It creates a classified GeoTIFF
    and a colored preview image.
    
    Args:
        image_id: Image identifier
        k: Number of classes (default: 5)
        max_iter: Maximum K-means iterations (default: 30)
        seed: Random seed for reproducibility (default: 0)
        
    Returns:
        Classification results summary with file paths
    """
    print(f"\n[classify_image_tool] Starting classification...")
    print(f"[classify_image_tool] Parameters: image_id={image_id}, k={k}, max_iter={max_iter}, seed={seed}")
    
    global image_service
    if image_service is None:
        error_msg = "Error: Image service not initialized"
        print(f"[classify_image_tool] {error_msg}")
        return error_msg
    
    if not RASTERIO_AVAILABLE:
        error_msg = "Error: rasterio is required for classification but not available"
        print(f"[classify_image_tool] {error_msg}")
        return error_msg
    
    try:
        # Get image metadata
        print(f"[classify_image_tool] Checking image metadata for {image_id}...")
        if image_id not in image_service._image_metadata:
            error_msg = f"Error: Image {image_id} not found"
            print(f"[classify_image_tool] {error_msg}")
            print(f"[classify_image_tool] Available image IDs: {list(image_service._image_metadata.keys())[:5]}...")
            return error_msg
        
        metadata = image_service._image_metadata[image_id]
        local_path = metadata["local_path"]
        print(f"[classify_image_tool] Found image metadata. Local path: {local_path}")
        
        # Check if file exists
        if not os.path.exists(local_path):
            error_msg = f"Error: Image file not found at {local_path}"
            print(f"[classify_image_tool] {error_msg}")
            return error_msg
        print(f"[classify_image_tool] Image file exists: {local_path}")
        
        # Check if it's a GeoTIFF
        ext = Path(local_path).suffix.lower()
        print(f"[classify_image_tool] File extension: {ext}")
        if ext not in [".tif", ".tiff"]:
            error_msg = f"Error: Classification only supports GeoTIFF files, got {ext}"
            print(f"[classify_image_tool] {error_msg}")
            return error_msg
        
        # Create output directory
        output_dir = Path(settings.upload_dir) / "classifications"
        output_dir.mkdir(exist_ok=True)
        print(f"[classify_image_tool] Output directory: {output_dir}")
        
        # Perform classification
        print(f"[classify_image_tool] Starting K-means classification (k={k}, max_iter={max_iter})...")
        result = kmeans_classify_raster(
            local_path,
            str(output_dir),
            k=k,
            max_iter=max_iter,
            seed=seed,
            save_masks=False
        )
        print(f"[classify_image_tool] Classification complete. Results: {list(result.keys())}")
        
        # Upload results to S3
        base_name = Path(local_path).stem
        classified_tif = result["classified_tif"]
        preview_png = result["preview_png"]
        print(f"[classify_image_tool] Classified TIF: {classified_tif}")
        print(f"[classify_image_tool] Preview PNG: {preview_png}")
        
        # Upload classified GeoTIFF
        print(f"[classify_image_tool] Uploading classified GeoTIFF to S3...")
        tif_s3_key = f"classifications/{image_id}/{Path(classified_tif).name}"
        upload_success = image_service.s3_client.upload_file(classified_tif, tif_s3_key, "image/tiff")
        print(f"[classify_image_tool] GeoTIFF upload {'successful' if upload_success else 'failed'}")
        tif_url = image_service.s3_client.generate_presigned_url(tif_s3_key, expires_in=86400)
        print(f"[classify_image_tool] GeoTIFF URL: {tif_url or tif_s3_key}")
        
        # Upload preview PNG
        print(f"[classify_image_tool] Uploading preview PNG to S3...")
        png_s3_key = f"classifications/{image_id}/{Path(preview_png).name}"
        upload_success = image_service.s3_client.upload_file(preview_png, png_s3_key, "image/png")
        print(f"[classify_image_tool] PNG upload {'successful' if upload_success else 'failed'}")
        png_url = image_service.s3_client.generate_presigned_url(png_s3_key, expires_in=86400)
        print(f"[classify_image_tool] PNG URL: {png_url or png_s3_key}")
        
        result_msg = (
            f"Classification complete for image {image_id}:\n"
            f"- Classes: {k}\n"
            f"- Classified GeoTIFF: {tif_url or tif_s3_key}\n"
            f"- Preview PNG: {png_url or png_s3_key}\n"
            f"- Local files: {classified_tif}, {preview_png}"
        )
        print(f"[classify_image_tool] Returning result message (length: {len(result_msg)} chars)")
        print(f"[classify_image_tool] Result preview: {result_msg[:200]}...")
        return result_msg
    except Exception as e:
        error_msg = f"Error classifying image: {str(e)}"
        print(f"[classify_image_tool] Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[classify_image_tool] Traceback:\n{traceback.format_exc()}")
        return error_msg


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
        self.tools = [analyze_image_tool, search_images_tool, classify_image_tool]
        # Bind tools to LLM
        self.agent = self.llm.bind_tools(self.tools)
        
        # Set global reference for tools
        set_image_service(image_service)
    
    def process_query(self, query: str, image_id: Optional[str] = None) -> Dict:
        """
        Process query using agent with tools.
        
        This implementation executes tool calls and feeds results back to the agent.
        
        Args:
            query: User query
            image_id: Optional specific image to analyze
            
        Returns:
            Dictionary with result, steps, and tools used
        """
        print(f"\n[AgentService.process_query] Starting query processing...")
        print(f"[AgentService.process_query] Query: {query}")
        print(f"[AgentService.process_query] Image ID: {image_id}")
        
        steps = []
        tools_used = []
        
        # If image_id provided, analyze it first
        if image_id:
            print(f"[AgentService.process_query] Pre-analyzing image {image_id}...")
            steps.append(f"Analyzing image {image_id}")
            try:
                analysis = self.image_service.analyze_image(image_id)
                steps.append(f"Analysis complete: {analysis.get('summary', '')}")
                tools_used.append("analyze_image_tool")
                print(f"[AgentService.process_query] Pre-analysis complete")
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                steps.append(error_msg)
                print(f"[AgentService.process_query] Pre-analysis error: {error_msg}")
        
        # Use agent to process query
        try:
            print(f"[AgentService.process_query] Invoking agent with query...")
            response = self.agent.invoke(query)
            print(f"[AgentService.process_query] Agent response received")
            print(f"[AgentService.process_query] Response type: {type(response)}")
            print(f"[AgentService.process_query] Response content: {response.content if hasattr(response, 'content') else 'N/A'}")
            print(f"[AgentService.process_query] Has tool_calls: {hasattr(response, 'tool_calls')}")
            
            # Create a tool map for execution
            tool_map = {tool.name: tool for tool in self.tools}
            
            # Handle tool calls iteratively
            max_iterations = 5  # Prevent infinite loops
            iteration = 0
            messages = [{"role": "user", "content": query}]
            
            while iteration < max_iterations:
                iteration += 1
                print(f"\n[AgentService.process_query] Iteration {iteration}")
                
                # Check if agent wants to use tools
                tool_calls = getattr(response, 'tool_calls', [])
                if not tool_calls:
                    print(f"[AgentService.process_query] No tool calls, finalizing response")
                    break
                
                print(f"[AgentService.process_query] Found {len(tool_calls)} tool call(s)")
                
                # Add assistant message with tool calls
                messages.append(response)
                
                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call.get('name', 'unknown')
                    tool_id = tool_call.get('id', 'unknown')
                    tool_args = tool_call.get('args', {})
                    
                    print(f"[AgentService.process_query] Executing tool: {tool_name}")
                    print(f"[AgentService.process_query] Tool ID: {tool_id}")
                    print(f"[AgentService.process_query] Tool args: {tool_args}")
                    
                    tools_used.append(tool_name)
                    steps.append(f"Tool called: {tool_name} with args: {tool_args}")
                    
                    if tool_name in tool_map:
                        try:
                            # Execute the tool
                            tool_func = tool_map[tool_name]
                            tool_result = tool_func.invoke(tool_args)
                            print(f"[AgentService.process_query] Tool result (first 200 chars): {str(tool_result)[:200]}...")
                            
                            # Add tool result to messages
                            messages.append({
                                "role": "tool",
                                "content": tool_result,
                                "tool_call_id": tool_id,
                                "name": tool_name
                            })
                        except Exception as e:
                            error_msg = f"Error executing {tool_name}: {str(e)}"
                            print(f"[AgentService.process_query] {error_msg}")
                            steps.append(error_msg)
                            messages.append({
                                "role": "tool",
                                "content": error_msg,
                                "tool_call_id": tool_id,
                                "name": tool_name
                            })
                    else:
                        error_msg = f"Unknown tool: {tool_name}"
                        print(f"[AgentService.process_query] {error_msg}")
                        steps.append(error_msg)
                
                # Get next response from agent
                print(f"[AgentService.process_query] Getting agent response with tool results...")
                response = self.agent.invoke(messages)
                print(f"[AgentService.process_query] Agent response content: {response.content if hasattr(response, 'content') else 'N/A'}")
            
            # Final result
            result = response.content if hasattr(response, 'content') else str(response)
            print(f"[AgentService.process_query] Final result length: {len(result)} chars")
            print(f"[AgentService.process_query] Final result preview: {result[:200]}...")
            steps.append(f"Final response: {result[:100]}...")
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(f"[AgentService.process_query] Exception: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[AgentService.process_query] Traceback:\n{traceback.format_exc()}")
            result = error_msg
            steps.append(error_msg)
        
        print(f"[AgentService.process_query] Returning result with {len(steps)} steps, {len(set(tools_used))} unique tools")
        return {
            "result": result,
            "steps": steps,
            "tools_used": list(set(tools_used))
        }


def set_image_service(service: ImageService) -> None:
    """Set global image service for tools."""
    global image_service
    image_service = service
