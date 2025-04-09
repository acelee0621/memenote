import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ForbiddenException

logger = get_logger(__name__)


s3_client = boto3.client(
    's3',
    endpoint_url=f"{'https' if settings.MINIO_USE_SSL else 'http'}://{settings.MINIO_ENDPOINT}",
    aws_access_key_id=settings.MINIO_ACCESS_KEY,
    aws_secret_access_key=settings.MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4'), # MinIO 通常需要 v4 签名
    # region_name 可以随便设置一个，例如 'us-east-1'，对于 MinIO 不重要
    region_name='us-east-1'
)


def ensure_minio_bucket_exists(bucket_name: str):
    try:
        # 检查 bucket 是否存在
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket '{bucket_name}' already exists.")
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "UnknownError")
        match error_code:
            case "NoSuchBucket":
                logger.error(f"Bucket '{bucket_name}' does not exist.")
                try:
                    s3_client.create_bucket(Bucket=bucket_name)
                    logger.info(f"Bucket '{bucket_name}' created successfully.")
                except Exception as create_error:
                    logger.error(f"Failed to create bucket '{bucket_name}': {str(create_error)}")
                    raise
            case "AccessDenied":
                logger.error(f"Permission denied to access bucket '{bucket_name}'")
                raise ForbiddenException("Permission denied to upload file")
            case _:
                logger.error(f"Unexpected error checking bucket '{bucket_name}': {str(e)}")
                raise