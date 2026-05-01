from typing import Any
from minio import Minio
from datetime import timedelta

class MinioService:
    def __init__(self, config: Any):
        # Configuration comes in as a dict from dependency-injector
        self._client = Minio(
            config.get("endpoint", "minio:9000"),
            access_key=config.get("access_key"),
            secret_key=config.get("secret_key"),
            secure=config.get("secure", False),
            region="us-east-1"
        )
        
        # A separate client specifically for generating presigned URLs for the browser.
        # Uses 'external_endpoint' for production domains, falling back to 'localhost' for local dev.
        self._presign_client = Minio(
            config.get("external_endpoint", "localhost:9000"),
            access_key=config.get("access_key"),
            secret_key=config.get("secret_key"),
            secure=config.get("secure", False),
            region="us-east-1"
        )
        
        self._bucket = config.get("bucket", "mapa-message-files")
        self._bucket_checked = False

    def _ensure_bucket(self):
        if self._bucket_checked:
            return
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
            self._bucket_checked = True
        except Exception as e:
            print(f"Minio: Warning - Could not ensure bucket: {e}")

    def get_presigned_upload_url(self, object_name: str, expires_in_minutes: int = 60) -> str:
        """Generates a pre-signed URL for client-side upload (PUT)"""
        self._ensure_bucket()
        try:
            return self._presign_client.presigned_put_object(
                self._bucket,
                object_name,
                expires=timedelta(minutes=expires_in_minutes)
            )
        except Exception as e:
            print(f"Minio Error: {e}")
            raise e

    def get_presigned_download_url(self, object_name: str, expires_in_minutes: int = 1440) -> str:
        """Generates a pre-signed URL for client-side download (GET)"""
        self._ensure_bucket()
        try:
            return self._presign_client.presigned_get_object(
                self._bucket,
                object_name,
                expires=timedelta(minutes=expires_in_minutes)
            )
        except Exception as e:
            print(f"Minio Error: {e}")
            raise e

    def delete_object(self, object_name: str):
        """Deletes an object from Minio"""
        try:
            self._client.remove_object(self._bucket, object_name)
        except Exception as e:
            print(f"Minio Error deleting {object_name}: {e}")
