"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app, tree_manager, storage
from app.tree_manager import TreeManager
from app.storage import LocalFileStorage


@pytest.fixture(autouse=True)
def reset_state(tmp_path):
    """Reset global state before each test."""
    global tree_manager, storage
    
    # Create fresh instances
    from app import main
    main.tree_manager = TreeManager()
    main.storage = LocalFileStorage(str(tmp_path / "test_trees.json"))
    
    yield
    
    # Cleanup
    main.tree_manager = TreeManager()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_empty_trees(client):
    """Test getting trees when database is empty."""
    response = client.get("/api/tree")
    assert response.status_code == 200
    assert response.json() == []


def test_create_root_node(client):
    """Test creating a root node."""
    response = client.post("/api/tree", json={"label": "root"})
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["label"] == "root"
    assert data["parent_id"] is None


def test_create_child_node(client):
    """Test creating a child node."""
    # Create root
    root_response = client.post("/api/tree", json={"label": "root"})
    root_id = root_response.json()["id"]
    
    # Create child
    child_response = client.post("/api/tree", json={
        "label": "child",
        "parent_id": root_id
    })
    
    assert child_response.status_code == 201
    child_data = child_response.json()
    assert child_data["label"] == "child"
    assert child_data["parent_id"] == root_id


def test_get_trees_with_hierarchy(client):
    """Test getting trees returns correct hierarchy matching spec example."""
    # Create tree structure from specification example
    # Tree: root -> bear -> cat
    # Note: IDs are sequential (1, 2, 3) not (1, 3, 4) as in spec example
    root_resp = client.post("/api/tree", json={"label": "root"})
    root_id = root_resp.json()["id"]

    bear_resp = client.post("/api/tree", json={"label": "bear", "parent_id": root_id})
    bear_id = bear_resp.json()["id"]

    cat_resp = client.post("/api/tree", json={"label": "cat", "parent_id": bear_id})
    cat_id = cat_resp.json()["id"]

    response = client.get("/api/tree")
    assert response.status_code == 200

    trees = response.json()
    assert len(trees) == 1

    # Verify structure matches spec example (labels and hierarchy)
    root = trees[0]
    assert root["id"] == root_id
    assert root["label"] == "root"
    assert len(root["children"]) == 1

    bear = root["children"][0]
    assert bear["id"] == bear_id
    assert bear["label"] == "bear"
    assert len(bear["children"]) == 1

    cat = bear["children"][0]
    assert cat["id"] == cat_id
    assert cat["label"] == "cat"
    assert len(cat["children"]) == 0


def test_create_node_parent_not_found(client):
    """Test error when parent doesn't exist."""
    response = client.post("/api/tree", json={
        "label": "orphan",
        "parent_id": 999
    })
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_node_invalid_label(client):
    """Test validation for empty label."""
    response = client.post("/api/tree", json={"label": ""})
    assert response.status_code == 422  # Validation error


def test_multiple_root_trees(client):
    """Test creating multiple root trees."""
    client.post("/api/tree", json={"label": "root1"})
    client.post("/api/tree", json={"label": "root2"})
    
    response = client.get("/api/tree")
    trees = response.json()
    
    assert len(trees) == 2
    assert trees[0]["label"] == "root1"
    assert trees[1]["label"] == "root2"


def test_api_documentation(client):
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert openapi["info"]["title"] == "HTTP Server Coding Challenge"

