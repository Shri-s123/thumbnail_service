import boto3
import logging
from botocore.exceptions import ClientError
from typing import Optional

lambda_client = boto3.client('lambda')


def add_api_gateway_permission_to_lambda(function_name: str, api_id: str, aws_region: str, aws_account_id: str) -> Optional[dict]:
    """
    Grants permission to API Gateway to invoke the specified Lambda function.

    This function creates a permission for API Gateway to invoke the Lambda function when an API endpoint
    is called. The permission is attached to the Lambda function using the 'add_permission' method.

    Args:
        function_name (str): The name of the Lambda function to which permission is being granted.
        api_id (str): The ID of the API Gateway to allow invoking the Lambda function.
        aws_region (str): The AWS region where the resources are located.
        aws_account_id (str): The AWS account ID of the account that owns the Lambda function.

    Returns:
        dict: The response from the Lambda `add_permission` API call if successful, or None if an error occurred.
    """
    try:
        response = lambda_client.add_permission(
            FunctionName=function_name,
            Principal='apigateway.amazonaws.com',
            StatementId='AllowAPIGatewayInvoke',
            Action='lambda:InvokeFunction',
            SourceArn=f'arn:aws:execute-api:{aws_region}:{aws_account_id}:{api_id}/*/*/*'
        )

        logging.info(f"Permission granted to API Gateway to invoke Lambda function '{function_name}'.")
        return response

    except ClientError as e:
        if 'ResourceConflictException' in str(e):
            return {"already exists":True}
        logging.error(f"Error granting permission to API Gateway for Lambda function '{function_name}': {e}")
        return None



def add_sqs_trigger_to_lambda(lambda_function_name: str, sqs_queue_arn: str) -> Optional[dict]:
    """
    Adds an SQS trigger to the specified Lambda function.

    This function creates an event source mapping between an SQS queue and a Lambda function, allowing the
    Lambda function to be triggered by messages in the specified SQS queue.

    Args:
        lambda_function_name (str): The name of the Lambda function to which the SQS queue will be connected.
        sqs_queue_arn (str): The ARN of the SQS queue that will trigger the Lambda function.

    Returns:
        dict: The response from the Lambda `create_event_source_mapping` API call if successful,
              or None if an error occurred.
    """
    try:
        response = lambda_client.create_event_source_mapping(
            EventSourceArn=sqs_queue_arn,
            FunctionName=lambda_function_name,
            Enabled=True,
            BatchSize=10
        )
        logging.info(f"Successfully added SQS trigger for '{lambda_function_name}' Lambda.")
        return response

    except Exception as e:
        if 'ResourceConflictException' in str(e):
            return {"already exists":True}
        logging.error(f"Error occurred in adding queue-lambda mapping: {str(e)}", exc_info=True)
        return None
