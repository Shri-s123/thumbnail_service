
# Service Layer - Image and thumbnails

This script automates the process of setting up AWS resources, including an S3 bucket, SQS queue, Lambda functions, and API Gateway for uploading, downloading images, and generating thumbnails.
It provides instagram like image upload functionality.

## Overview:
The architecture is designed to handle multiple concurrent requests, ensuring scalability, asynchronous processing, and high availability.

## Components:
- **API Gateway + Lambda:** Handles multiple concurrent requests by scaling horizontally.
- **S3:** Provides high availability and durability for storing images and thumbnails.
- **SQS:** Decouples the image upload and thumbnail processing. Ensures no data loss during high traffic.

## Architecture

![alt text](others/Service_Layer_Thumbnail.drawio.png)


## Functional Block Diagram

#### **/upload API**

                            +------------------------+
                            |    API Gateway         |
                            |------------------------|
                            |  /upload (POST)        |
                            +------------------------+
                                      |
                                      v
                         +--------------------------+
                         |     Lambda Function 1    |
                         |--------------------------|
                         | - Handles image uploads  |
                         | - Stores images in S3    |
                         | - Sends message to SQS   |
                         +--------------------------+
                                      |
                                      v
                          +-----------------------+
                          |    Amazon S3 Bucket   |
                          |-----------------------|
                          | - Stores original     |
                          |   images              |
                          | - Stores thumbnails   |
                          +-----------------------+
                                      ^
                                      |
                         +-------------------------+
                         |     Amazon SQS Queue    |
                         |-------------------------|
                         | - Receives image upload |
                         |   messages              |
                         +-------------------------+
                                      |
                                      v
                         +--------------------------+
                         |    Lambda Function 2     |
                         |--------------------------|
                         | - Listens to SQS Queue   |
                         | - Generates thumbnail    |
                         | - Stores thumbnail in S3 |
                         +--------------------------+

	
	
#### **/download image API**

                            +-------------------------------+
                            |    API Gateway                |
                            |-------------------------------|
                            |  /download/{image-name}(GET)  |
                            +-------------------------------+
                                      |
                                      v
                         +----------------------------------+
                         |     Lambda Function 3            |
                         |----------------------------------|
                         | - Gets the image object from s3  |
                         +----------------------------------+
                                     
                        

#### **/download-thumbnail API**

		 	        +-----------------------------------+
                            |    API Gateway                    |
                            |-----------------------------------|
                            |  /download-thumbnail/{image-name} |
			        | 		(GET)               |
                            +-----------------------------------+
                                      |
                                      v
                         +----------------------------------+
                         |     Lambda Function 4            |
                         |----------------------------------|
                         | - Gets the thumbnail object of   |
			     |      image stored in s3          |
                         +----------------------------------+
                                     


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
python main.py
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



