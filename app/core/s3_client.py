import boto3
from botocore.client import Config

from app.core.config import settings


s3_client = boto3.client(
    's3',
    endpoint_url=f"{'https' if settings.MINIO_USE_SSL else 'http'}://{settings.MINIO_ENDPOINT}",
    aws_access_key_id=settings.MINIO_ACCESS_KEY,
    aws_secret_access_key=settings.MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4'), # MinIO 通常需要 v4 签名
    # region_name 可以随便设置一个，例如 'us-east-1'，对于 MinIO 不重要
    region_name='us-east-1'
)