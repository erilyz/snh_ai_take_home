"""Data models for tree structures."""

from typing import List, Optional
from pydantic import BaseModel, Field


class TreeNode(BaseModel):
    """Represents a node in the tree structure."""
    
    id: int = Field(..., description="Unique identifier for the node")
    label: str = Field(..., description="Label/name of the node")
    children: List["TreeNode"] = Field(default_factory=list, description="Child nodes")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "label": "root",
                "children": [
                    {
                        "id": 2,
                        "label": "child",
                        "children": []
                    }
                ]
            }
        }


class CreateNodeRequest(BaseModel):
    """Request model for creating a new node."""
    
    label: str = Field(..., description="Label for the new node", min_length=1)
    parent_id: Optional[int] = Field(None, description="ID of parent node. If None, creates a new root node")

    class Config:
        json_schema_extra = {
            "example": {
                "label": "new_node",
                "parent_id": 1
            }
        }


class CreateNodeResponse(BaseModel):
    """Response model for node creation."""
    
    id: int = Field(..., description="ID of the newly created node")
    label: str = Field(..., description="Label of the newly created node")
    parent_id: Optional[int] = Field(None, description="ID of the parent node")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 3,
                "label": "new_node",
                "parent_id": 1
            }
        }

