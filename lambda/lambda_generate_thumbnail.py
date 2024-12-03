import boto3
import json


s3 = boto3.client('s3')

def lambda_handler(event, context):
    """"""
    try:
        for record in event['Records']:
            message_body = json.loads(record['body'])
            bucket_name = message_body['bucket']
            s3_key = message_body['key']


            # Get the object from S3
            s3_object = s3.get_object(Bucket=bucket_name, Key=s3_key)
            image_data = s3_object['Body'].read()

            # thumbnail generation
            thumbnail_key = s3_key.rsplit('.', 1)[0] + '-thumbnail' + s3_key[s3_key.rfind('.'): ]

            # Upload the same file with the new name
            s3.put_object(Bucket=bucket_name, Key=thumbnail_key, Body=image_data)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Thumbnail generated and uploaded successfully.'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error generating thumbnail: {str(e)}'})
        }
