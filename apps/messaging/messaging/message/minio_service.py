from typing import Any
from minio import Minio
from datetime import timedelta

class MinioService:
    def __init__(self, config: Any):
        # Configuration comes in as a dict from dependency-injector
        def _clean_endpoint(endpoint: str, default_secure: bool = False) -> tuple[str, bool]:
            if not endpoint:
                return "localhost:9000", default_secure
            is_secure = default_secure
            if "://" in endpoint:
                scheme, endpoint = endpoint.split("://", 1)
                if scheme.lower() == "https":
                    is_secure = True
                elif scheme.lower() == "http":
                    is_secure = False
            endpoint = endpoint.strip("/")
            endpoint = endpoint.replace("/:", ":")
            if "/" in endpoint:
                endpoint = endpoint.split("/")[0]
            return endpoint, is_secure

        raw_endpoint = config.get("endpoint", "minio:9000")
        raw_secure = config.get("secure", False)
        endpoint, secure = _clean_endpoint(raw_endpoint, raw_secure)

        self._client = Minio(
            endpoint,
            access_key=config.get("access_key"),
            secret_key=config.get("secret_key"),
            secure=secure,
            region="us-east-1"
        )
        
        # A separate client specifically for generating presigned URLs for the browser.
        # Uses 'external_endpoint' for production domains, falling back to 'localhost' for local dev.
        raw_ext_endpoint = config.get("external_endpoint", "localhost:9000")
        ext_endpoint, ext_secure = _clean_endpoint(raw_ext_endpoint, raw_secure)

        self._presign_client = Minio(
            ext_endpoint,
            access_key=config.get("access_key"),
            secret_key=config.get("secret_key"),
            secure=ext_secure,
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
            
            import json
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self._bucket}/*"]
                    }
                ]
            }
            self._client.set_bucket_policy(self._bucket, json.dumps(policy))

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
