"""Main FastAPI application for HTTP server coding challenge."""

import logging
import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from app.logging_config import setup_logging
from app.models import TreeNode, CreateNodeRequest, CreateNodeResponse
from app.storage import create_storage_backend, StorageBackend, StorageError
from app.tree_manager import TreeManager

# Setup logging
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Global state
storage: StorageBackend = None
tree_manager: TreeManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    global storage, tree_manager
    
    # Startup
    logger.info("Starting Tree API server")
    
    try:
        # Initialize storage backend
        storage_type = os.getenv("STORAGE_TYPE", "local")
        storage_config = _get_storage_config(storage_type)
        storage = create_storage_backend(storage_type, **storage_config)
        logger.info(f"Storage backend initialized: {storage_type}")
        
        # Initialize tree manager and load data
        tree_manager = TreeManager()
        data = storage.load()
        tree_manager.load_state(data)
        logger.info("Tree manager initialized and data loaded")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Tree API server")


def _get_storage_config(storage_type: str) -> dict:
    """Get storage configuration from environment variables.
    
    Args:
        storage_type: Type of storage backend
        
    Returns:
        Dictionary of configuration parameters
    """
    if storage_type == "local":
        return {"file_path": os.getenv("STORAGE_PATH", "data/trees.json")}
    elif storage_type == "gcs":
        return {
            "bucket_name": os.getenv("GCS_BUCKET_NAME"),
            "object_name": os.getenv("GCS_OBJECT_NAME", "trees.json")
        }
    elif storage_type == "s3":
        return {
            "bucket_name": os.getenv("S3_BUCKET_NAME"),
            "object_key": os.getenv("S3_OBJECT_KEY", "trees.json"),
            "region": os.getenv("AWS_REGION")
        }
    return {}


# Create FastAPI app
app = FastAPI(
    title="HTTP Server Coding Challenge",
    description="Production-ready HTTP API for managing hierarchical tree data structures",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint to verify API and storage are operational.
    
    Returns:
        Health status with storage connectivity check
    """
    storage_healthy = storage.health_check() if storage else False
    
    if not storage_healthy:
        logger.warning("Health check failed: storage not accessible")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "storage": "unavailable"
            }
        )
    
    return {
        "status": "healthy",
        "storage": "available"
    }


@app.get("/api/tree", response_model=List[TreeNode], status_code=status.HTTP_200_OK)
async def get_trees():
    """Get all trees from the database.
    
    Returns:
        List of all root trees with their hierarchical structure
    """
    try:
        trees = tree_manager.get_all_trees()
        logger.info(f"Retrieved {len(trees)} trees")
        return trees
    except Exception as e:
        logger.error(f"Failed to retrieve trees: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trees"
        )


@app.post("/api/tree", response_model=CreateNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(request: CreateNodeRequest):
    """Create a new node and attach it to a specified parent node.
    
    Args:
        request: Node creation request with label and optional parent_id
        
    Returns:
        Information about the newly created node
        
    Raises:
        HTTPException: If parent not found or storage fails
    """
    try:
        # Create the node
        new_node = tree_manager.create_node(request.label, request.parent_id)
        
        # Persist to storage
        try:
            storage.save(tree_manager.get_state())
        except StorageError as e:
            logger.error(f"Failed to persist data: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save data to storage"
            )
        
        return CreateNodeResponse(
            id=new_node.id,
            label=new_node.label,
            parent_id=request.parent_id
        )
        
    except ValueError as e:
        # Parent not found
        logger.warning(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create node: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create node"
        )

