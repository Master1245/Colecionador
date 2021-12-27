import boto3
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
SECRET_KEY = os.environ.get("aws_access_key_id")
DATABASE_PASSWORD = os.environ.get("aws_secret_access_key")
LOCATION = os.environ.get("region_name")

s3 = boto3.client('s3', aws_access_key_id=SECRET_KEY, aws_secret_access_key=DATABASE_PASSWORD, region_name=LOCATION)
response = s3.generate_presigned_url('get_object',Params={'Bucket': 'colecionador','Key': 'pbkdf2:sha256:260000$JkhuHxSspfvFcxw5$7b795746aef1a8f84e7bb69a3efe724d6844cbdf9b1b02fe4785457ed49ed364.jfif'},ExpiresIn=None)
print(response)