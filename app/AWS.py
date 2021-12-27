import boto3
import os
from dotenv import load_dotenv, find_dotenv
from werkzeug.security import generate_password_hash

local = os.path.dirname(os.path.abspath(__file__))


load_dotenv(find_dotenv())
SECRET_KEY = os.environ.get("aws_access_key_id")
DATABASE_PASSWORD = os.environ.get("aws_secret_access_key")
LOCATION = os.environ.get("region_name")



def get_img(img_name):
    s3 = boto3.client('s3', aws_access_key_id=SECRET_KEY, aws_secret_access_key=DATABASE_PASSWORD, region_name=LOCATION)
    response = s3.generate_presigned_url('get_object',Params={'Bucket': 'colecionador','Key': img_name},ExpiresIn=3600)
    print(response)

def upload_img(img_name):
    s3 = boto3.client('s3', aws_access_key_id=SECRET_KEY, aws_secret_access_key=DATABASE_PASSWORD, region_name=LOCATION)
    s3.upload_file(f"./CARDS/{img_name}", 'colecionador', generate_password_hash(img_name))

upload_img("download.jfif")