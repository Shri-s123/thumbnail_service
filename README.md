
# Service Layer - Image and thumbnails

This script automates the process of setting up AWS resources, including an S3 bucket, SQS queue, Lambda functions, and API Gateway for uploading, downloading images, and generating thumbnails.
It provides instagram like image upload functionality.

## Features:
- **S3 Bucket**: Creates an S3 bucket for image storage.
- **SQS Queue**: Creates an SQS queue for message handling.
- **Lambda Functions**:
  - Upload Image (`lambda_upload`)
  - Download Image (`lambda_download_image`)
  - Generate Thumbnail (`lambda_generate_thumbnail`)
  - Download Thumbnail (`lambda_download_thumbnail`)
- **API Gateway**: Creates API endpoints for uploading, downloading images, and downloading thumbnails.

## Prerequisites:
- AWS CLI configured with valid credentials.
- Python 3.12+.
- Required Python libraries: `boto3`.

## Installation:
1. Install required libraries:
   ```bash
   pip install boto3
   ```

2. Set up your `config/config.py` file with necessary AWS configurations:
   ```python
   AWS_REGION = 'your-region'
   AWS_ACCOUNT_ID = 'your-account-id'
   S3_BUCKET_NAME = 'your-s3-bucket-name'
   SQS_QUEUE_NAME = 'your-sqs-queue-name'
   API_GATEWAY_NAME = 'your-api-gateway-name'
   UPLOAD_LAMBDA_FUNCTION_NAME = 'your-upload-lambda-function-name'
   DOWNLOAD_LAMBDA_FUNCTION_NAME = 'your-download-lambda-function-name'
   THUMBNAIL_LAMBDA_FUNCTION_NAME = 'your-thumbnail-lambda-function-name'
   DOWNLOAD_THUMBNAIL_LAMBDA_FUNCTION_NAME = 'your-download-thumbnail-lambda-function-name'
   ```

## Usage:
Run the script to create all necessary resources:

```bash
python create_resources.py
```

The script will:
- Create an S3 bucket.
- Set up an SQS queue.
- Create Lambda functions.
- Set up API Gateway with endpoints:
  - `/upload`: Upload image (POST)
  - `/download/{file_name}`: Download image (GET)
  - `/download-thumbnail/{file_name}`: Download thumbnail (GET)
- Add necesary permissions for lambda, sqs and apigateway.

## Notes:
- This script uses `boto3` for interacting with AWS services.

