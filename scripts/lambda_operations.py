import boto3
import os
import zipfile
import logging
from typing import Optional
from botocore.exceptions import ClientError

lambda_client = boto3.client('lambda')


def package_lambda_function(lambda_code_path: str, config_code_path: str, zip_filename: str) -> None:
    """
    Packages the Lambda function code into a zip file.

    This function compresses the source code of the Lambda function (including any dependencies in the
    provided directory) into a zip file, ready to be uploaded to AWS Lambda.

    Args:
        lambda_code_path (str): The local directory path containing the Lambda function source code files.
        zip_filename (str): The path and name of the zip file to create, which will contain the Lambda code.

    Returns:
        None: If the function is successful, it does not return any value.
    """
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(lambda_code_path, os.path.basename(lambda_code_path))
            zipf.write(config_code_path, os.path.basename(config_code_path))
        logging.info(f"Packaged Lambda function code into '{zip_filename}'.")
    except ClientError as e:
        logging.error(f"Error packaging Lambda function: {e.response['Error']['Message']}", exc_info=True)


def create_lambda_function(function_name: str, handler_name: str, role_arn: str = None) -> Optional[str]:
    """
    Creates and deploys a new Lambda function.

    This function packages the Lambda function code into a zip file, uploads it to AWS Lambda,
    and creates the function using the provided handler and role information.

    Args:
        function_name (str): The name of the Lambda function to create in AWS.
        handler_name (str): The name of the handler within the Lambda function code (i.e., 'file_name.lambda_handler').
        role_arn (str, optional): The ARN of the IAM role to be assigned to the Lambda function.
                                  If not provided, the role assignment is skipped.

    Returns:
        Optional[str]: The ARN of the created Lambda function if successful, or None if an error occurs.
    """
    # Get the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Go one level up to access the 'lambda' and 'config' directories
    thumbnail_service = os.path.dirname(script_dir)
    lambda_code_path = os.path.join(thumbnail_service, 'lambda', f'{handler_name}.py')
    config_code_path = os.path.join(thumbnail_service, 'config', 'config.py')

    # Normalize the file paths
    lambda_code_path = os.path.normpath(lambda_code_path)
    config_code_path = os.path.normpath(config_code_path)

    if not os.path.exists(lambda_code_path):
        logging.error(f"Error: Lambda code file {lambda_code_path} does not exist.")
        return None

    if not os.path.exists(config_code_path):
        logging.error(f"Error: Config file {config_code_path} does not exist.")
        return None

    # Build the path for the zip file
    zip_filename = os.path.join(thumbnail_service, 'lambda', f'{handler_name}.zip')
    zip_filename = os.path.normpath(zip_filename)

    package_lambda_function(lambda_code_path, config_code_path, zip_filename)

    with open(zip_filename, 'rb') as f:
        zip_data = f.read()

    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.12',
            Role=role_arn,
            Handler=f'{handler_name}.lambda_handler',
            Code={'ZipFile': zip_data},
            Timeout=15,
            MemorySize=128,
        )
        logging.info(f"Lambda function '{function_name}' created successfully.")
        return response['FunctionArn']

    except ClientError as e:
        if 'Function already exist' in str(e):
            return "created"
        logging.error(f"Error creating Lambda function '{function_name}': {e.response['Error']['Message']}",
                      exc_info=True)
        return None

    finally:
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
            logging.info(f"Deleted temporary zip file '{zip_filename}'.")
