"""Tests for TreeManager class."""

import pytest
from app.tree_manager import TreeManager
from app.models import TreeNode


def test_create_root_node():
    """Test creating a root node."""
    manager = TreeManager()
    node = manager.create_node("root")
    
    assert node.id == 1
    assert node.label == "root"
    assert len(node.children) == 0
    assert len(manager.get_all_trees()) == 1


def test_create_child_node():
    """Test creating a child node."""
    manager = TreeManager()
    root = manager.create_node("root")
    child = manager.create_node("child", parent_id=root.id)
    
    assert child.id == 2
    assert child.label == "child"
    assert len(root.children) == 1
    assert root.children[0].id == child.id


def test_create_multiple_roots():
    """Test creating multiple root trees."""
    manager = TreeManager()
    root1 = manager.create_node("root1")
    root2 = manager.create_node("root2")
    
    trees = manager.get_all_trees()
    assert len(trees) == 2
    assert trees[0].id == root1.id
    assert trees[1].id == root2.id


def test_create_nested_children():
    """Test creating nested child nodes."""
    manager = TreeManager()
    root = manager.create_node("root")
    child1 = manager.create_node("child1", parent_id=root.id)
    child2 = manager.create_node("child2", parent_id=child1.id)
    
    assert len(root.children) == 1
    assert len(root.children[0].children) == 1
    assert root.children[0].children[0].id == child2.id


def test_parent_not_found():
    """Test error when parent node doesn't exist."""
    manager = TreeManager()
    
    with pytest.raises(ValueError, match="Parent node with id 999 not found"):
        manager.create_node("orphan", parent_id=999)


def test_load_and_get_state():
    """Test loading and getting state."""
    manager = TreeManager()
    manager.create_node("root")
    manager.create_node("child", parent_id=1)
    
    # Get state
    state = manager.get_state()
    assert state["next_id"] == 3
    assert len(state["trees"]) == 1
    
    # Load into new manager
    new_manager = TreeManager()
    new_manager.load_state(state)
    
    assert new_manager.next_id == 3
    assert len(new_manager.get_all_trees()) == 1
    assert len(new_manager.get_all_trees()[0].children) == 1


def test_load_invalid_state():
    """Test error handling for invalid state data."""
    manager = TreeManager()
    
    with pytest.raises(ValueError, match="Invalid tree data format"):
        manager.load_state({"trees": [{"invalid": "data"}]})


def test_incremental_ids():
    """Test that IDs increment correctly."""
    manager = TreeManager()
    
    for i in range(1, 6):
        node = manager.create_node(f"node{i}")
        assert node.id == i
    
    assert manager.next_id == 6

