import requests

image_name = 'img.png'

# Replace this with your API Gateway URL and append the query string
API_GATEWAY_URL = f'https://53a1m0nwui.execute-api.us-east-1.amazonaws.com/dev/download-thumbnail?file_name={image_name}'

# Send GET request to the API Gateway
response = requests.get(API_GATEWAY_URL)

# Check if the request was successful
if response.status_code == 200:
    # Save the file to the local system
    with open(image_name, 'wb') as file:
        file.write(response.content)
    print(f'File "{image_name}" downloaded successfully.')
else:
    print(f'Failed to download file. HTTP Status Code: {response.status_code}')
