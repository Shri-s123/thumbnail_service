import requests
import base64

API_GATEWAY_URL = 'https://xb5r31iptc.execute-api.us-east-1.amazonaws.com/dev/upload'

image_path = './test_resources/img.png'



# Read the image file and encode it to base64
def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

file_content = encode_image_to_base64(image_path)


payload = {
    "file": {
        "filename": "img.png",
        "content": file_content,  # Base64 encoded content of the image with proper padding
        "content_type": "image/png"
    }
}

# Headers for the request
headers = {
    'Content-Type': 'application/json',
}

# Send POST request to API Gateway
response = requests.post(API_GATEWAY_URL, json=payload, headers=headers)

# Print the response
if response.status_code == 200:
    print("Upload successful:", response.json())
else:
    print("Error:", response.status_code, response.text)
