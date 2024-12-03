import logging
from config.config import *
from iam_operations import create_iam_role
from s3_operations import create_s3_bucket
from sqs_operations import create_sqs_queue
from lambda_operations import create_lambda_function
from utils import add_api_gateway_permission_to_lambda
from utils import add_sqs_trigger_to_lambda
from apigateway_operations import create_api_gateway
import time

# Set up logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('deployment_log.txt')  # Logs to file
    ]
)


def main(bucket_name: str,
         queue_name: str,
         role_name: str,
         lambda_functions: list,
         api_gateway_name: str,
         aws_region: str,
         aws_account_id: str,
         upload_lambda: str,
         thumbnail_generate_lambda: str):
    """
    Main function to orchestrate the creation of an S3 bucket, IAM role, Lambda functions, SQS queue, and API Gateway.

    Args:
        bucket_name (str): The name of the S3 bucket to be created.
        queue_name (str): The name of the SQS queue to be created.
        role_name (str): The name of the IAM role to be created.
        lambda_functions (list): A list of tuples, where each tuple contains the Lambda function name and handler name.
        api_gateway_name (str): The name of the API Gateway to be created.
        aws_region (str): The AWS region where the resources will be created.
        aws_account_id (str): The AWS account ID.
        upload_lambda (str): The name of the Lambda function to handle image uploads.
        thumbnail_generate_lambda (str): The name of the Lambda function to handle thumbnail generation.

    Returns:
        None
    """

    # Step 1: Create S3 bucket
    logging.info(f"Creating S3 bucket: {bucket_name}...")
    bucket_url = create_s3_bucket(bucket_name)
    if not bucket_url:
        logging.error("Failed to create S3 bucket. Exiting...")
        return

    # Step 2: Create SQS Queue
    logging.info(f"Creating SQS queue: {queue_name}...")
    queue_url = create_sqs_queue(queue_name)
    if not queue_url:
        logging.error("Failed to create SQS queue. Exiting...")
        return

    # Step 3: Create IAM role with Trust and Permissions policy
    logging.info(f"Creating IAM role: {role_name}...")
    trust_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }

    permissions_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:ListBucket",
                    "sqs:SendMessage",
                    "sqs:ReceiveMessage",
                    "sqs:DeleteMessage",
                    "sqs:GetQueueAttributes",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "*"
            }
        ]
    }
    role_arn = create_iam_role(role_name, trust_policy_document, permissions_policy_document, aws_account_id)
    if not role_arn:
        logging.error("Failed to create IAM role. Exiting...")
        return

    # Step 4: Create Lambda functions
    time.sleep(15) #LambdaExecutionRole to be fully available

    logging.info("Creating Lambda functions...")
    for function_name, handler_name, _ in lambda_functions:
        lambda_arn = create_lambda_function(function_name, handler_name, role_arn)
        if not lambda_arn:
            logging.error(f"Failed to create Lambda function: {function_name}. Exiting...")
            return
        logging.info(f"Lambda function '{function_name}' created successfully.")

    # Step 5: Create API Gateway and link it to the Lambda functions
    logging.info(f"Creating API Gateway: {api_gateway_name}...")
    api_gateway_url, api_id = create_api_gateway(api_gateway_name, lambda_functions, aws_region, aws_account_id)
    if not api_gateway_url:
        logging.error("Failed to create API Gateway. Exiting...")
        return

    # Step 6: Grant permissions to API Gateway to invoke Lambda functions
    for function_name, handler_name, path_part in lambda_functions:
        gateway_permission_response = add_api_gateway_permission_to_lambda(function_name, api_id, aws_region,
                                                                           aws_account_id)
        if not gateway_permission_response:
            logging.error("Failed to add permissions to API Gateway. Exiting...")
            return


    queue_arn = f'arn:aws:sqs:{aws_region}:{aws_account_id}:{queue_name}'
    sqs_trigger_response = add_sqs_trigger_to_lambda(thumbnail_generate_lambda, queue_arn)
    if not sqs_trigger_response:
        logging.error("Failed to add permissions to SQS queue. Exiting...")
        return

    # Summary
    logging.info("Setup complete.")

    # Log the API URLs and their purposes
    logging.info("API URLs and their purposes:")
    logging.info(f"1. Upload Image: {api_gateway_url}upload (POST) - Uploads an image to S3")
    logging.info(f"2. Download Image: {api_gateway_url}download/{{file_name}} (GET) - Downloads an image from S3")
    logging.info(
        f"3. Download Thumbnail: {api_gateway_url}download-thumbnail/{{file_name}} (GET) - Downloads a thumbnail of "
        f"an image")


if __name__ == "__main__":
    main(
        bucket_name=S3_BUCKET_NAME,
        queue_name=SQS_QUEUE_NAME,
        role_name=LAMBDA_ROLE_NAME,
        lambda_functions=[
            (UPLOAD_LAMBDA_FUNCTION_NAME, UPLOAD_HANDLER, UPLOAD_PART),
            (DOWNLOAD_LAMBDA_FUNCTION_NAME, DOWNLOAD_HANDLER, DOWNLOAD_PART),
            (THUMBNAIL_LAMBDA_FUNCTION_NAME, THUMBNAIL_GENERATE_HANDLER, None),
            (DOWNLOAD_THUMBNAIL_LAMBDA_FUNCTION_NAME, DOWNLOAD_THUMBNAIL_HANDLER,DOWNLOAD_THUMBNAIL_PART)
        ],
        api_gateway_name=API_GATEWAY_NAME,
        aws_region=AWS_REGION,
        aws_account_id=AWS_ACCOUNT_ID,
        upload_lambda=UPLOAD_LAMBDA_FUNCTION_NAME,
        thumbnail_generate_lambda=UPLOAD_LAMBDA_FUNCTION_NAME
    )
