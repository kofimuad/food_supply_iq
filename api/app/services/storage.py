"""S3-compatible object storage for visit photos (Story 3.3).

Provider-agnostic: targets local MinIO in dev and Cloudflare R2 / Railway-MinIO
in prod via the S3_* settings. Uploads use presigned PUT URLs (client uploads
directly to storage); viewing uses presigned GET URLs.
"""

import uuid
from functools import lru_cache

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.config import get_settings

settings = get_settings()

UPLOAD_URL_TTL = 900  # 15 min to upload
VIEW_URL_TTL = 3600  # 1 hour to view


@lru_cache
def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        # Path-style addressing works with MinIO and R2 on a custom endpoint.
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


@lru_cache
def _ensure_bucket() -> None:
    """Create the bucket if missing (best-effort; cached so it runs once)."""
    if not settings.s3_auto_create_bucket:
        return
    client = _client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        try:
            client.create_bucket(Bucket=settings.s3_bucket)
        except ClientError:
            pass  # already exists / no permission — leave to ops


def build_key(visit_id: uuid.UUID, content_type: str | None) -> str:
    ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(
        content_type or "", "bin"
    )
    return f"visits/{visit_id}/{uuid.uuid4().hex}.{ext}"


def presign_put(key: str, content_type: str | None) -> str:
    _ensure_bucket()
    params = {"Bucket": settings.s3_bucket, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    return _client().generate_presigned_url(
        "put_object", Params=params, ExpiresIn=UPLOAD_URL_TTL
    )


def presign_get(key: str) -> str:
    return _client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=VIEW_URL_TTL,
    )


def delete_object(key: str) -> None:
    try:
        _client().delete_object(Bucket=settings.s3_bucket, Key=key)
    except ClientError:
        pass
