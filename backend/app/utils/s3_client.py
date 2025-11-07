"""S3 client utilities for image storage and retrieval."""
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from typing import Optional
import io
import os


class S3Client:
    """Client for AWS S3 operations."""
    
    def __init__(self, bucket_name: str, region: str = "us-west-1", 
                 access_key_id: Optional[str] = None, 
                 secret_access_key: Optional[str] = None):
        """
        Initialize S3 client.
        
        Args:
            bucket_name: S3 bucket name
            region: AWS region
            access_key_id: AWS access key ID (if None, uses env vars)
            secret_access_key: AWS secret access key (if None, uses env vars)
        """
        self.bucket_name = bucket_name
        
        # Use provided credentials or fall back to environment variables
        if access_key_id and secret_access_key:
            self.s3_client = boto3.client(
                "s3",
                region_name=region,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key
            )
        else:
            # boto3 will automatically use AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from env
            # But let's ensure they're set
            if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
                raise ValueError(
                    "AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY "
                    "environment variables or pass them to S3Client."
                )
            self.s3_client = boto3.client("s3", region_name=region)
    
    def upload_file(self, file_path: str, s3_key: str, content_type: str = "image/jpeg") -> bool:
        """
        Upload file to S3.
        
        Args:
            file_path: Local file path
            s3_key: S3 object key
            content_type: MIME type
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={"ContentType": content_type, "ACL": "private"}
            )
            return True
        except (BotoCoreError, ClientError) as e:
            print(f"Upload failed: {e}")
            return False
    
    def upload_bytes(self, data: bytes, s3_key: str, content_type: str = "image/jpeg") -> bool:
        """
        Upload bytes to S3.
        
        Args:
            data: File data as bytes
            s3_key: S3 object key
            content_type: MIME type
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=data,
                ContentType=content_type,
                ACL="private"
            )
            return True
        except (BotoCoreError, ClientError) as e:
            print(f"Upload failed: {e}")
            return False
    
    def generate_presigned_url(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for S3 object.
        
        Args:
            s3_key: S3 object key
            expires_in: URL expiration time in seconds
            
        Returns:
            Presigned URL or None on error
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expires_in
            )
            return url
        except (BotoCoreError, ClientError) as e:
            print(f"URL generation failed: {e}")
            return None

