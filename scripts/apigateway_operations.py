import boto3
import logging
from botocore.exceptions import ClientError
from typing import List, Tuple, Optional, Any

apigateway_client = boto3.client('apigateway')
lambda_client = boto3.client('lambda')


def create_api_gateway(
        api_gateway_name: str,
        lambda_function_names: List[Tuple[str, str]],  # List of tuples with (path_part, lambda_function_name)
        aws_region: str,
        aws_account_id: str
) -> tuple[str, Any] | None:
    """
    Creates an API Gateway, integrates it with multiple Lambda functions, and deploys the API.

    Args:
        api_gateway_name (str): The name of the API Gateway to create.
        lambda_function_names (List[Tuple[str, str]]): A list of tuples containing the path part (e.g., 'upload', 'download')
                                                      and the corresponding Lambda function name.
        aws_region (str): The AWS region where the API Gateway and Lambda functions are located.
        aws_account_id (str): The AWS account ID.

    Returns:
        Optional[str]: The URL of the deployed API if successful, None otherwise.
    """
    try:
        # Create a REST API
        logging.info(f"Creating API Gateway '{api_gateway_name}'...")
        api_response = apigateway_client.create_rest_api(
            name=api_gateway_name,
            description='API to upload images, download images, and thumbnails',
        )
        api_id = api_response['id']
        logging.info(f"API Gateway '{api_gateway_name}' created with ID: {api_id}")

        # Root resource
        logging.info("Fetching root resources...")
        resources_response = apigateway_client.get_resources(
            restApiId=api_id
        )
        root_resource_id = resources_response['items'][0]['id']

        # Iterate over Lambda function names to create resources and methods
        for function_name, handler_name, path_part in lambda_function_names:
            if function_name=="image-thumbnail-generate":
                continue
            logging.info(f"Creating resource and method for path: {path_part} with Lambda function: {function_name}")

            # Create resource (e.g., /upload, /download)
            resource_response = apigateway_client.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart=path_part
            )
            logging.info(f"Resource '{path_part}' created with ID: {resource_response['id']}")

            # Determine HTTP method (POST for upload, GET for download)
            method = 'POST' if path_part == 'upload' else 'GET'
            apigateway_client.put_method(
                restApiId=api_id,
                resourceId=resource_response['id'],
                httpMethod=method,
                authorizationType='NONE'
            )
            logging.info(f"Method '{method}' created for resource '{path_part}'.")

            # Integrate the resource with the respective Lambda function
            apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=resource_response['id'],
                httpMethod=method,
                integrationHttpMethod='POST',
                type='AWS_PROXY',
                uri=f'arn:aws:apigateway:{aws_region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{aws_region}:{aws_account_id}:function:{function_name}/invocations'
            )
            logging.info(f"Lambda function '{function_name}' integrated with resource '{path_part}'.")

        stage_name = 'dev'
        logging.info(f"Deploying API Gateway to stage '{stage_name}'...")
        apigateway_client.create_deployment(
            restApiId=api_id,
            stageName=stage_name
        )
        logging.info(f"API Gateway deployed successfully to stage '{stage_name}'.")

        # Get the URL for the API
        api_url = f'https://{api_id}.execute-api.{aws_region}.amazonaws.com/{stage_name}/'

        # Log the API URLs and their associated Lambda functions
        logging.info("API URLs and their associated Lambda functions:")
        for function_name, _, path_part in lambda_function_names:
            method = 'POST' if path_part == 'upload' else 'GET'
            logging.info(f"{method} {api_url}{path_part} - {function_name}")

        return api_url, api_id

    except ClientError as e:
        logging.error(f"Error creating API Gateway: {e.response['Error']['Message']}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}", exc_info=True)
        return None
