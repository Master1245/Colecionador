import boto3
import os
from dotenv import load_dotenv, find_dotenv
from werkzeug.security import generate_password_hash

local = os.path.dirname(os.path.abspath(__file__))

load_dotenv(find_dotenv())
# SECRET_KEY = os.environ.get("aws_access_key_id")
# ACESS_ID = os.environ.get("aws_secret_access_key")
# LOCATION = os.environ.get("region_name")

SECRET_KEY = os.environ['aws_access_key_id']
ACESS_ID = os.environ['aws_secret_access_key']
LOCATION = os.environ['region_name']


def get_img(img_name):
    s3 = boto3.client('s3', aws_access_key_id=SECRET_KEY, aws_secret_access_key=ACESS_ID, region_name=LOCATION)
    response = s3.generate_presigned_url('get_object',Params={'Bucket': 'colecionador','Key': img_name + ".jpg"},ExpiresIn=3600)
    return response

def upload_img(img_name, hash):
    s3 = boto3.client('s3', aws_access_key_id=SECRET_KEY, aws_secret_access_key=ACESS_ID, region_name=LOCATION)
    s3.upload_file(f"./CARDS/{img_name}", 'colecionador', hash+".jpg", ExtraArgs={'ContentType': "image/jpeg"})

def delete_img(img_name):
    s3 = boto3.client('s3', aws_access_key_id=SECRET_KEY, aws_secret_access_key=ACESS_ID, region_name=LOCATION)
    s3.delete_object(Bucket='colecionador', Key=img_name+".jpg")