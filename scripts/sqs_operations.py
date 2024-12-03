import boto3
import logging
from typing import Optional
from botocore.exceptions import ClientError

sqs_client = boto3.client('sqs')


def create_sqs_queue(queue_name: str) -> Optional[str]:
    """
    Creates an SQS queue with the specified name in AWS.

    This function uses the `create_queue` method from the AWS SDK to create a queue. If the queue is successfully
    created, it returns the URL of the created queue. If the creation fails, it logs the error and returns None.

    Args:
        queue_name (str): The name of the SQS queue to create.

    Returns:
        Optional[str]: The URL of the created SQS queue if successful, or None if creation failed.
    """
    try:
        response = sqs_client.create_queue(QueueName=queue_name)
        logging.info(f"SQS queue '{queue_name}' created successfully.")
        return response['QueueUrl']
    except ClientError as e:
        logging.error(f"Error creating SQS queue '{queue_name}': {e}", exc_info=True)
        return None
