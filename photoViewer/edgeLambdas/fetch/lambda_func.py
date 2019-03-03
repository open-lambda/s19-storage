BUCKET_NAME = 'cs839'

import traceback
import sys
sys.path.insert(0, '/packages')
import urllib3

import base64
import boto3
import botocore

def handler(event):
  try:
    session = boto3.Session(aws_access_key_id = event['aws_access_key_id'],
                            aws_secret_access_key = event['aws_secret_access_key'])
    s3 = session.resource('s3')
    obj = s3.Object(BUCKET_NAME, event['file_name'])
    return base64.b64encode(obj.get()['Body'].read()).decode('ascii')
  except Exception as e:
    return {'python_version': sys.version, 'sys_path': sys.path, 'urllib3_version':urllib3.__version__, 'error': str(e), 'traceback': traceback.format_exc()} 
