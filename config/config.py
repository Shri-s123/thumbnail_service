import os


AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID', '125452764654')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'image-thumbnail-bucket-shri')
SQS_QUEUE_NAME = os.getenv('SQS_QUEUE_NAME', 'ImageThumbnailQueue')
UPLOAD_LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'image-upload')
DOWNLOAD_LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'image-download')
DOWNLOAD_THUMBNAIL_LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'image-thumbnail')
THUMBNAIL_LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'image-thumbnail-generate')

API_GATEWAY_NAME = os.getenv('API_GATEWAY_NAME', 'ImageUploadAPI')


