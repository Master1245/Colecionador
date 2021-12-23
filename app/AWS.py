import boto3


def upload(file):
    s3 = boto3.resource('s3')
    BUCKET = "test"

    s3.Bucket(BUCKET).upload_file("your/local/file", "dump/file")