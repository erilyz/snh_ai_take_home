"""Tests for storage backends."""

import json
import pytest
from pathlib import Path
from app.storage import LocalFileStorage, StorageError


@pytest.fixture
def temp_storage_path(tmp_path):
    """Provide a temporary storage path."""
    return tmp_path / "test_trees.json"


def test_local_storage_save_and_load(temp_storage_path):
    """Test saving and loading data with local storage."""
    storage = LocalFileStorage(str(temp_storage_path))
    
    test_data = {
        "trees": [{"id": 1, "label": "root", "children": []}],
        "next_id": 2
    }
    
    storage.save(test_data)
    loaded_data = storage.load()
    
    assert loaded_data == test_data


def test_local_storage_load_nonexistent(temp_storage_path):
    """Test loading when file doesn't exist returns empty state."""
    storage = LocalFileStorage(str(temp_storage_path))
    data = storage.load()
    
    assert data == {"trees": [], "next_id": 1}


def test_local_storage_corrupted_file(temp_storage_path):
    """Test error handling for corrupted JSON file."""
    storage = LocalFileStorage(str(temp_storage_path))
    
    # Write invalid JSON
    temp_storage_path.parent.mkdir(parents=True, exist_ok=True)
    temp_storage_path.write_text("invalid json{")
    
    with pytest.raises(StorageError, match="Corrupted data file"):
        storage.load()


def test_local_storage_atomic_write(temp_storage_path):
    """Test that writes are atomic (temp file + rename)."""
    storage = LocalFileStorage(str(temp_storage_path))
    
    test_data = {"trees": [], "next_id": 1}
    storage.save(test_data)
    
    # Verify temp file doesn't exist after save
    temp_file = temp_storage_path.with_suffix('.tmp')
    assert not temp_file.exists()
    assert temp_storage_path.exists()


def test_local_storage_health_check(temp_storage_path):
    """Test health check for local storage."""
    storage = LocalFileStorage(str(temp_storage_path))
    assert storage.health_check() is True


def test_local_storage_creates_directory(tmp_path):
    """Test that storage creates parent directories if needed."""
    nested_path = tmp_path / "nested" / "dir" / "trees.json"
    storage = LocalFileStorage(str(nested_path))
    
    test_data = {"trees": [], "next_id": 1}
    storage.save(test_data)
    
    assert nested_path.exists()
    assert nested_path.parent.exists()

