"""Tree management logic for creating and querying tree structures."""

import logging
from typing import List, Optional, Dict, Any
from app.models import TreeNode

logger = logging.getLogger(__name__)


class TreeManager:
    """Manages tree data structures with in-memory operations."""
    
    def __init__(self):
        """Initialize the tree manager with empty state."""
        self.trees: List[TreeNode] = []
        self.next_id: int = 1
        self._node_map: Dict[int, TreeNode] = {}  # Fast lookup by ID
    
    def load_state(self, data: Dict[str, Any]) -> None:
        """Load tree state from persisted data.
        
        Args:
            data: Dictionary containing 'trees' and 'next_id'
        """
        try:
            self.trees = [TreeNode(**tree) for tree in data.get("trees", [])]
            self.next_id = data.get("next_id", 1)
            self._rebuild_node_map()
            logger.info(f"Loaded {len(self.trees)} trees, next_id={self.next_id}")
        except Exception as e:
            logger.error(f"Failed to load state: {e}", exc_info=True)
            raise ValueError(f"Invalid tree data format: {e}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current tree state for persistence.
        
        Returns:
            Dictionary containing 'trees' and 'next_id'
        """
        return {
            "trees": [tree.model_dump() for tree in self.trees],
            "next_id": self.next_id
        }
    
    def get_all_trees(self) -> List[TreeNode]:
        """Get all trees.
        
        Returns:
            List of all root trees
        """
        return self.trees
    
    def create_node(self, label: str, parent_id: Optional[int] = None) -> TreeNode:
        """Create a new node and attach it to a parent or as a new root.
        
        Args:
            label: Label for the new node
            parent_id: ID of parent node, or None to create a new root
            
        Returns:
            The newly created node
            
        Raises:
            ValueError: If parent_id is provided but parent not found
        """
        new_node = TreeNode(id=self.next_id, label=label, children=[])
        self.next_id += 1
        
        if parent_id is None:
            # Create new root tree
            self.trees.append(new_node)
            self._node_map[new_node.id] = new_node
            logger.info(f"Created new root node: id={new_node.id}, label={label}")
        else:
            # Find parent and attach
            parent = self._find_node(parent_id)
            if parent is None:
                logger.warning(f"Parent node not found: parent_id={parent_id}")
                raise ValueError(f"Parent node with id {parent_id} not found")
            
            parent.children.append(new_node)
            self._node_map[new_node.id] = new_node
            logger.info(f"Created child node: id={new_node.id}, label={label}, parent_id={parent_id}")
        
        return new_node
    
    def _find_node(self, node_id: int) -> Optional[TreeNode]:
        """Find a node by ID using the node map.
        
        Args:
            node_id: ID of the node to find
            
        Returns:
            The node if found, None otherwise
        """
        return self._node_map.get(node_id)
    
    def _rebuild_node_map(self) -> None:
        """Rebuild the node map from current trees for fast lookups."""
        self._node_map.clear()
        
        def add_to_map(node: TreeNode):
            self._node_map[node.id] = node
            for child in node.children:
                add_to_map(child)
        
        for tree in self.trees:
            add_to_map(tree)

