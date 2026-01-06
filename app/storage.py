"""Storage abstraction layer supporting local filesystem, GCS, and S3."""

import json
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Load data from storage.
        
        Returns:
            Dictionary containing tree data
            
        Raises:
            StorageError: If loading fails
        """
        pass
    
    @abstractmethod
    def save(self, data: Dict[str, Any]) -> None:
        """Save data to storage.
        
        Args:
            data: Dictionary containing tree data
            
        Raises:
            StorageError: If saving fails
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if storage backend is accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        pass


class StorageError(Exception):
    """Exception raised for storage-related errors."""
    pass


class LocalFileStorage(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, file_path: str = "data/trees.json"):
        """Initialize local file storage.
        
        Args:
            file_path: Path to the JSON file for storage
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized LocalFileStorage: {self.file_path}")
    
    def load(self) -> Dict[str, Any]:
        """Load data from local file."""
        try:
            if not self.file_path.exists():
                logger.info("No existing data file, starting fresh")
                return {"trees": [], "next_id": 1}
            
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded data from {self.file_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.file_path}: {e}")
            raise StorageError(f"Corrupted data file: {e}")
        except Exception as e:
            logger.error(f"Failed to load from {self.file_path}: {e}")
            raise StorageError(f"Failed to load data: {e}")
    
    def save(self, data: Dict[str, Any]) -> None:
        """Save data to local file with atomic write."""
        try:
            # Atomic write: write to temp file, then rename
            temp_path = self.file_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self.file_path)
            logger.info(f"Saved data to {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save to {self.file_path}: {e}")
            raise StorageError(f"Failed to save data: {e}")
    
    def health_check(self) -> bool:
        """Check if local storage is accessible."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            return os.access(self.file_path.parent, os.W_OK)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


class GCSStorage(StorageBackend):
    """Google Cloud Storage backend."""

    def __init__(self, bucket_name: str, object_name: str = "trees.json"):
        """Initialize GCS storage.

        Args:
            bucket_name: Name of the GCS bucket
            object_name: Name of the object in the bucket
        """
        try:
            from google.cloud import storage
            self.client = storage.Client()
            self.bucket = self.client.bucket(bucket_name)
            self.object_name = object_name
            logger.info(f"Initialized GCSStorage: gs://{bucket_name}/{object_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise StorageError(f"GCS initialization failed: {e}")

    def load(self) -> Dict[str, Any]:
        """Load data from GCS."""
        try:
            blob = self.bucket.blob(self.object_name)
            if not blob.exists():
                logger.info("No existing data in GCS, starting fresh")
                return {"trees": [], "next_id": 1}

            data = json.loads(blob.download_as_text())
            logger.info(f"Loaded data from GCS: {self.object_name}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in GCS object: {e}")
            raise StorageError(f"Corrupted data in GCS: {e}")
        except Exception as e:
            logger.error(f"Failed to load from GCS: {e}")
            raise StorageError(f"Failed to load from GCS: {e}")

    def save(self, data: Dict[str, Any]) -> None:
        """Save data to GCS."""
        try:
            blob = self.bucket.blob(self.object_name)
            blob.upload_from_string(
                json.dumps(data, indent=2),
                content_type='application/json'
            )
            logger.info(f"Saved data to GCS: {self.object_name}")
        except Exception as e:
            logger.error(f"Failed to save to GCS: {e}")
            raise StorageError(f"Failed to save to GCS: {e}")

    def health_check(self) -> bool:
        """Check if GCS bucket is accessible."""
        try:
            return self.bucket.exists()
        except Exception as e:
            logger.error(f"GCS health check failed: {e}")
            return False


class S3Storage(StorageBackend):
    """AWS S3 storage backend."""

    def __init__(self, bucket_name: str, object_key: str = "trees.json", region: Optional[str] = None):
        """Initialize S3 storage.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: Key of the object in the bucket
            region: AWS region (optional, uses default if not specified)
        """
        try:
            import boto3
            self.s3_client = boto3.client('s3', region_name=region)
            self.bucket_name = bucket_name
            self.object_key = object_key
            logger.info(f"Initialized S3Storage: s3://{bucket_name}/{object_key}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise StorageError(f"S3 initialization failed: {e}")

    def load(self) -> Dict[str, Any]:
        """Load data from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=self.object_key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            logger.info(f"Loaded data from S3: {self.object_key}")
            return data
        except self.s3_client.exceptions.NoSuchKey:
            logger.info("No existing data in S3, starting fresh")
            return {"trees": [], "next_id": 1}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in S3 object: {e}")
            raise StorageError(f"Corrupted data in S3: {e}")
        except Exception as e:
            logger.error(f"Failed to load from S3: {e}")
            raise StorageError(f"Failed to load from S3: {e}")

    def save(self, data: Dict[str, Any]) -> None:
        """Save data to S3."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=self.object_key,
                Body=json.dumps(data, indent=2).encode('utf-8'),
                ContentType='application/json'
            )
            logger.info(f"Saved data to S3: {self.object_key}")
        except Exception as e:
            logger.error(f"Failed to save to S3: {e}")
            raise StorageError(f"Failed to save to S3: {e}")

    def health_check(self) -> bool:
        """Check if S3 bucket is accessible."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except Exception as e:
            logger.error(f"S3 health check failed: {e}")
            return False


def create_storage_backend(storage_type: str = "local", **kwargs) -> StorageBackend:
    """Factory function to create storage backend based on type.

    Args:
        storage_type: Type of storage ('local', 'gcs', or 's3')
        **kwargs: Additional arguments for the storage backend

    Returns:
        Configured storage backend instance

    Raises:
        ValueError: If storage_type is invalid
    """
    if storage_type == "local":
        return LocalFileStorage(**kwargs)
    elif storage_type == "gcs":
        return GCSStorage(**kwargs)
    elif storage_type == "s3":
        return S3Storage(**kwargs)
    else:
        raise ValueError(f"Invalid storage type: {storage_type}. Must be 'local', 'gcs', or 's3'")

