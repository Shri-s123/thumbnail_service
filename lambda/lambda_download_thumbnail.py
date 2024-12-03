import boto3
import base64
from config import *
import json

s3 = boto3.client('s3')
bucket_name = S3_BUCKET_NAME


def lambda_handler(event, context):
    try:
        # Get the file name from the API path parameters
        file_name = event['queryStringParameters']['file_name']

        s3_key = file_name.rsplit('.', 1)[0] + '-thumbnail' + file_name[file_name.rfind('.'):]
        s3_object = s3.get_object(Bucket=bucket_name, Key=s3_key)
        image_data = s3_object['Body'].read()

        # Encode the image as base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        return {
            'statusCode': 200,
            'body': json.dumps({'image_data': image_base64})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error downloading image: {str(e)}'})
        }
