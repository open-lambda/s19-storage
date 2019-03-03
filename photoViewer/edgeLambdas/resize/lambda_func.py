BUCKET_NAME = 'cs839'
import traceback
import sys
sys.path.insert(0, '/packages')
import urllib3
import base64
import boto3
import botocore
from io import BytesIO
def handler(event):
  try:
    from PIL import Image
    session = boto3.Session(aws_access_key_id = event['aws_access_key_id'],
                            aws_secret_access_key = event['aws_secret_access_key'])
    s3 = session.resource('s3')
    obj = s3.Object(BUCKET_NAME, event['file_name'])
    data = obj.get()['Body'].read()
    img = Image.open(BytesIO(data))
    resized_image = img.resize((event['width'], event['height']))
    result = BytesIO()
    resized_image.save(result, "JPEG")
    base64_result = base64.b64encode(result.getvalue()).decode('ascii')
    return base64_result
  except Exception as e:
    return {'python_version': sys.version, 'sys_path': sys.path, 'urllib3_version':urllib3.__version__, 'error': str(e), 'traceback': traceback.format_exc()} 
