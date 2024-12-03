import zipfile

import boto3
import json
from config.config import *

# Initialize boto3 clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
sqs_client = boto3.client('sqs', region_name=AWS_REGION)
lambda_client = boto3.client('lambda', region_name=AWS_REGION)
apigateway_client = boto3.client('apigateway', region_name=AWS_REGION)
iam_client = boto3.client('iam', region_name=AWS_REGION)


# Create S3 Bucket
def create_s3_bucket():
    try:
        response = s3_client.create_bucket(
            Bucket=S3_BUCKET_NAME
        )
        print(f"S3 bucket '{S3_BUCKET_NAME}' created successfully.")
        return response
    except Exception as e:
        print(f"Error creating S3 bucket: {str(e)}")


# Create SQS Queue
def create_sqs_queue():
    try:
        response = sqs_client.create_queue(QueueName=SQS_QUEUE_NAME)
        queue_url = response['QueueUrl']
        print(f"SQS Queue '{SQS_QUEUE_NAME}' created successfully.")
        return queue_url
    except Exception as e:
        print(f"Error creating SQS queue: {str(e)}")


# Create Lambda Execution Role
def create_lambda_role():
    role_policy = {
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

    try:
        response = iam_client.create_role(
            RoleName='LambdaExecutionRole',
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        }
                    }
                ]
            })
        )
        iam_client.put_role_policy(
            RoleName='LambdaExecutionRole',
            PolicyName='LambdaExecutionPolicy',
            PolicyDocument=json.dumps(role_policy)
        )
        print("Lambda Execution Role created successfully.")
        return response
    except Exception as e:
        print(f"Error creating Lambda role: {str(e)}")


# Create Lambda Function
def create_lambda_function(function_name, handler_name, role_arn=None):
    # Get the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Go one level up to access the 'lambda' directory
    thumbnail_service = os.path.dirname(script_dir)  # One level above

    lambda_code_path = os.path.join(thumbnail_service, 'lambda', f'{handler_name}.py')
    config_code_path = os.path.join(thumbnail_service, 'config','config.py')


    # avoid any double slashes
    lambda_code_path = os.path.normpath(lambda_code_path)
    config_code_path = os.path.normpath(config_code_path)

    if not os.path.exists(lambda_code_path):
        print(f"Error: Lambda code file {lambda_code_path} does not exist.")
        return

    if not os.path.exists(config_code_path):
        print(f"Error: Config file {config_code_path} does not exist.")
        return

    # Build the path for the zip file
    zip_filename = os.path.join(thumbnail_service, 'lambda', f'{handler_name}.zip')
    zip_filename = os.path.normpath(zip_filename)

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(lambda_code_path, os.path.basename(lambda_code_path))
        zipf.write(config_code_path, os.path.basename(config_code_path))

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
        print(f"Lambda function '{function_name}' created successfully.")

        os.remove(zip_filename)
        print(f"Deleted temporary zip file '{zip_filename}'.")

    except Exception as e:
        print(f"Error creating Lambda function: {str(e)}")


# Grant permission to API Gateway to invoke Lambda function
def add_api_gateway_permission_to_lambda(function_name, api_id):
    try:
        response = lambda_client.add_permission(
            FunctionName=function_name,
            Principal='apigateway.amazonaws.com',
            StatementId=f'{api_id}-invoke-permission',
            Action='lambda:InvokeFunction',
            SourceArn=f'arn:aws:execute-api:{AWS_REGION}:{AWS_ACCOUNT_ID}:{api_id}/*/*/*'
        )
        print(f"Permission granted to API Gateway to invoke Lambda function '{function_name}'.")
        return response
    except Exception as e:
        print(f"Error granting permission to API Gateway: {str(e)}")


# Allow Lambda to send messages to SQS
def add_lambda_permission_for_sqs(function_name):
    try:
        response = lambda_client.add_permission(
            FunctionName=function_name,
            Principal='sqs.amazonaws.com',
            StatementId=f'{function_name}-sqs-send-permission',
            Action='lambda:InvokeFunction',
            SourceArn=f'arn:aws:sqs:{AWS_REGION}:{AWS_ACCOUNT_ID}:{SQS_QUEUE_NAME}'
        )
        print(f"Permission granted to Lambda '{function_name}' to send messages to SQS.")
        return response
    except Exception as e:
        print(f"Error granting SQS permission to Lambda '{function_name}': {str(e)}")


# Allow SQS to trigger Lambda (for generate-thumbnail Lambda)
def add_sqs_trigger_to_lambda(lambda_function_name, sqs_queue_arn):
    try:
        response = lambda_client.create_event_source_mapping(
            EventSourceArn=sqs_queue_arn,
            FunctionName=lambda_function_name,
            Enabled=True,
            BatchSize=10
        )
        print(f"Successfully added SQS trigger for '{lambda_function_name}' Lambda.")
        return response
    except Exception as e:
        print(f"Error adding SQS trigger for '{lambda_function_name}' Lambda: {str(e)}")


def create_api_gateway():
    # Create a REST API
    api_response = apigateway_client.create_rest_api(
        name=API_GATEWAY_NAME,
        description='API to upload images, download images and thumbnails',
    )
    api_id = api_response['id']

    #    root resource
    resources_response = apigateway_client.get_resources(
        restApiId=api_id
    )
    root_resource_id = resources_response['items'][0]['id']

    # Create the /upload resource
    upload_resource_response = apigateway_client.create_resource(
        restApiId=api_id,
        parentId=root_resource_id,
        pathPart='upload'
    )

    # Create the /upload method (POST)
    apigateway_client.put_method(
        restApiId=api_id,
        resourceId=upload_resource_response['id'],
        httpMethod='POST',
        authorizationType='NONE'
    )

    # Integrate the /upload method with Lambda. Use post to lambda
    apigateway_client.put_integration(
        restApiId=api_id,
        resourceId=upload_resource_response['id'],
        httpMethod='POST',
        integrationHttpMethod='POST',
        type='AWS_PROXY',
        uri=f'arn:aws:apigateway:{AWS_REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT_ID}:function:{UPLOAD_LAMBDA_FUNCTION_NAME}/invocations'
    )

    # Create /download/{file_name} resource
    download_resource_response = apigateway_client.create_resource(
        restApiId=api_id,
        parentId=root_resource_id,
        pathPart='download'
    )

    # Create the /download method (GET)
    apigateway_client.put_method(
        restApiId=api_id,
        resourceId=download_resource_response['id'],
        httpMethod='GET',
        authorizationType='NONE'
    )

    apigateway_client.put_integration(
        restApiId=api_id,
        resourceId=download_resource_response['id'],
        httpMethod='GET',
        integrationHttpMethod='POST',
        type='AWS_PROXY',
        uri=f'arn:aws:apigateway:{AWS_REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT_ID}:function:{DOWNLOAD_LAMBDA_FUNCTION_NAME}/invocations'
    )

    # Create /download-thumbnail/{file_name} resource
    thumbnail_resource_response = apigateway_client.create_resource(
        restApiId=api_id,
        parentId=root_resource_id,
        pathPart='download-thumbnail'
    )

    # Create the /download-thumbnail method (GET)
    apigateway_client.put_method(
        restApiId=api_id,
        resourceId=thumbnail_resource_response['id'],
        httpMethod='GET',
        authorizationType='NONE'
    )

    # Integrate /download-thumbnail with Lambda
    apigateway_client.put_integration(
        restApiId=api_id,
        resourceId=thumbnail_resource_response['id'],
        httpMethod='GET',
        integrationHttpMethod='GET',
        type='AWS_PROXY',
        uri=f'arn:aws:apigateway:{AWS_REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT_ID}:function:{DOWNLOAD_THUMBNAIL_LAMBDA_FUNCTION_NAME}/invocations'
    )
    print(f"Successfully created api gateway api_id:{api_id}.")

    # Deploy API
    stage_name = 'dev'
    deployment_response = apigateway_client.create_deployment(
        restApiId=api_id,
        stageName=stage_name
    )

    # Get the URL for the API
    api_url = f'https://{api_id}.execute-api.{AWS_REGION}.amazonaws.com/{stage_name}/'

    print("API URLs and their purposes:")
    print(f"1. Upload Image: {api_url}upload (POST) - Uploads an image to S3")
    print(f"2. Download Image: {api_url}download/{{file_name}} (GET) - Downloads an image from S3")
    print(f"3. Download Thumbnail: {api_url}download-thumbnail/{{file_name}} (GET) - Downloads a thumbnail of an image")

    return api_id


# Main function to create all resources
def create_resources():
    create_s3_bucket()
    queue_url = create_sqs_queue()

    role_response = create_lambda_role()
    role_arn = role_response['Role']['Arn']

    # Create Lambda functions
    create_lambda_function(UPLOAD_LAMBDA_FUNCTION_NAME, 'lambda_upload', role_arn)
    create_lambda_function(DOWNLOAD_LAMBDA_FUNCTION_NAME, 'lambda_download_image', role_arn)
    create_lambda_function(THUMBNAIL_LAMBDA_FUNCTION_NAME, 'lambda_generate_thumbnail',role_arn)
    create_lambda_function(DOWNLOAD_THUMBNAIL_LAMBDA_FUNCTION_NAME, 'lambda_download_thumbnail', role_arn)

    api_id = create_api_gateway()

    # Grant API Gateway permission to invoke Lambda functions
    add_api_gateway_permission_to_lambda(UPLOAD_LAMBDA_FUNCTION_NAME, api_id)
    add_api_gateway_permission_to_lambda(DOWNLOAD_LAMBDA_FUNCTION_NAME, api_id)
    add_api_gateway_permission_to_lambda(THUMBNAIL_LAMBDA_FUNCTION_NAME, api_id)
    add_api_gateway_permission_to_lambda(DOWNLOAD_THUMBNAIL_LAMBDA_FUNCTION_NAME, api_id)

    # Grant SQS permission for Lambda to send messages
    add_lambda_permission_for_sqs(UPLOAD_LAMBDA_FUNCTION_NAME)

    # Grant SQS permission to invoke generate-thumbnail Lambda
    sqs_queue_arn = f'arn:aws:sqs:{AWS_REGION}:{AWS_ACCOUNT_ID}:{SQS_QUEUE_NAME}'
    add_sqs_trigger_to_lambda(THUMBNAIL_LAMBDA_FUNCTION_NAME, sqs_queue_arn)



if __name__ == "__main__":
    create_resources()
