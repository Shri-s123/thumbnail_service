import os


AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID', '125452764654')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'image-thumbnail-bucket-shri')
SQS_QUEUE_NAME = os.getenv('SQS_QUEUE_NAME', 'ImageThumbnailQueue')
LAMBDA_ROLE_NAME = os.getenv('LAMBDA_ROLE_NAME','MyLambdaExecutionRole')
UPLOAD_LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'image-upload')
DOWNLOAD_LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'image-download')
DOWNLOAD_THUMBNAIL_LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'image-thumbnail')
THUMBNAIL_LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'image-thumbnail-generate')
UPLOAD_HANDLER = os.getenv('UPLOAD_HANDLER', 'lambda_upload')
DOWNLOAD_HANDLER = os.getenv('DOWNLOAD_HANDLER', 'lambda_download_image')
DOWNLOAD_THUMBNAIL_HANDLER = os.getenv('DOWNLOAD_THUMBNAIL_HANDLER', 'lambda_download_thumbnail')
THUMBNAIL_GENERATE_HANDLER = os.getenv('THUMBNAIL_GENERATE_HANDLER', 'lambda_generate_thumbnail')
UPLOAD_PART = 'upload'
DOWNLOAD_PART ='download'
DOWNLOAD_THUMBNAIL_PART = 'download-thumbnail'
API_GATEWAY_NAME = os.getenv('API_GATEWAY_NAME', 'ImageUploadAPI')



