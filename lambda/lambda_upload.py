import json
import boto3
from config import *
import base64
import logging

# Initialize S3 and SQS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
sqs_client = boto3.client('sqs', region_name=AWS_REGION)

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def correct_base64_padding(encoded_str):
    # Add the correct padding to base64 string if it's not padded correctly
    padding = len(encoded_str) % 4
    if padding != 0:
        encoded_str += '=' * (4 - padding)
    return encoded_str


def lambda_handler(event, context):
    try:
        logger.info("Lambda function started.")

        # Parse the body of the request
        body = json.loads(event['body'])
        logger.info(f"Request body: {body}")

        if 'file' not in body:
            logger.error("No file provided in the request")
            raise ValueError('No file provided in the request')

        file = body['file']

        # Validate file type
        if not allowed_file(file['filename']):
            logger.error(f"Invalid file type: {file['filename']}")
            raise ValueError('File format not allowed. Allowed formats are: png, jpg, jpeg, gif')

        logger.info(f"File {file['filename']} passed validation.")

        # Correct the padding if necessary
        corrected_content = correct_base64_padding(file['content'])
        # Decode base64 content
        file_content = base64.b64decode(corrected_content)
        logger.info(f"File {file['filename']} decoded successfully.")

        # Upload to S3
        s3_response = s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file['filename'],
            Body=file_content,  # The decoded file content
            ContentType=file['content_type']
        )
        logger.info(f"File {file['filename']} uploaded to S3 successfully.")
        print('uploaded')

        # Send a message to SQS for thumbnail generation
        sqs_message = {
            'bucket': S3_BUCKET_NAME,
            'key': file['filename']
        }

        sqs_client.send_message(
            QueueUrl=SQS_QUEUE_NAME,
            MessageBody=json.dumps(sqs_message)
        )
        logger.info(f"Message sent to SQS for file {file['filename']}.")

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"File {file['filename']} uploaded successfully.",
                'file_url': f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{file['filename']}"
            })
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f"Error: {str(e)}"})
        }
