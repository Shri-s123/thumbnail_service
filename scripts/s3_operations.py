import boto3
import logging
from typing import Optional
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')


def create_s3_bucket(bucket_name: str) -> Optional[str]:
    """
    Creates an S3 bucket in the specified AWS region.

    This function creates an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket to create.

    Returns:
        Optional[str]: The URL of the created S3 bucket in the format 's3://bucket_name/',
                       or None if the bucket creation failed.
    """
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        logging.info(f"S3 bucket '{bucket_name}' created successfully.")
        return f"s3://{bucket_name}/"  # Returning the S3 bucket URL
    except ClientError as e:
        logging.error(f"Error creating S3 bucket '{bucket_name}': {e}", exc_info=True)
        return None
