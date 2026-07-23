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
        
        # A separate client specifically for generating presigned URLs for the browser/clients.
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
        
        self._bucket = config.get("bucket", "mapa-desktop-mobile-files")
        self._bucket_checked = set()

    def _ensure_bucket(self, bucket: str = None):
        target_bucket = bucket or self._bucket
        if target_bucket in self._bucket_checked:
            return
        try:
            if not self._client.bucket_exists(target_bucket):
                self._client.make_bucket(target_bucket)
            self._bucket_checked.add(target_bucket)
        except Exception as e:
            print(f"Minio: Warning - Could not ensure bucket '{target_bucket}': {e}")

    def get_presigned_upload_url(self, object_name: str, expires_in_minutes: int = 60, bucket: str = None) -> str:
        """Generates a pre-signed URL for client-side upload (PUT)"""
        target_bucket = bucket or self._bucket
        self._ensure_bucket(target_bucket)
        try:
            return self._presign_client.presigned_put_object(
                target_bucket,
                object_name,
                expires=timedelta(minutes=expires_in_minutes)
            )
        except Exception as e:
            print(f"Minio Error generating upload URL: {e}")
            raise e

    def get_presigned_download_url(self, object_name: str, expires_in_minutes: int = 1440, bucket: str = None) -> str:
        """Generates a pre-signed URL for client-side download (GET)"""
        target_bucket = bucket or self._bucket
        self._ensure_bucket(target_bucket)
        try:
            return self._presign_client.presigned_get_object(
                target_bucket,
                object_name,
                expires=timedelta(minutes=expires_in_minutes)
            )
        except Exception as e:
            print(f"Minio Error: {e}")
            raise e

    def delete_object(self, object_name: str, bucket: str = None):
        """Deletes an object from Minio"""
        target_bucket = bucket or self._bucket
        try:
            self._client.remove_object(target_bucket, object_name)
        except Exception as e:
            print(f"Minio Error deleting {object_name} from {target_bucket}: {e}")

    def delete_prefix(self, prefix: str, bucket: str = None):
        """Deletes all objects under a prefix from Minio (recursive deletion)"""
        target_bucket = bucket or self._bucket
        try:
            objects = self._client.list_objects(target_bucket, prefix=prefix, recursive=True)
            for obj in objects:
                self._client.remove_object(target_bucket, obj.object_name)
        except Exception as e:
            print(f"Minio Error deleting prefix {prefix} from {target_bucket}: {e}")

    def list_objects(self, prefix: str, bucket: str = None) -> list:
        """Lists objects under a prefix from Minio"""
        target_bucket = bucket or self._bucket
        try:
            return list(self._client.list_objects(target_bucket, prefix=prefix, recursive=True))
        except Exception as e:
            print(f"Minio Error listing prefix {prefix} from {target_bucket}: {e}")
            return []

    def get_object(self, object_name: str, bucket: str = None) -> bytes:
        """Downloads an object from Minio"""
        target_bucket = bucket or self._bucket
        try:
            response = self._client.get_object(target_bucket, object_name)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()
        except Exception as e:
            print(f"Minio Error getting {object_name} from {target_bucket}: {e}")
            raise e

    def put_object(self, object_name: str, data: bytes, content_type: str = "application/octet-stream", bucket: str = None):
        """Uploads an object to Minio"""
        from io import BytesIO
        target_bucket = bucket or self._bucket
        self._ensure_bucket(target_bucket)
        try:
            self._client.put_object(
                target_bucket,
                object_name,
                BytesIO(data),
                length=len(data),
                content_type=content_type
            )
        except Exception as e:
            print(f"Minio Error putting {object_name} to {target_bucket}: {e}")
            raise e
