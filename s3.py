import boto3
from constants import S3_ACCESS_KEY, S3_ACCESS_SECRET, S3_BUCKET_NAME

def s3_bucket():
    session = boto3.Session(aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_ACCESS_SECRET)
    return session.resource('s3').Bucket(S3_BUCKET_NAME) # pylint: disable=E1101

def upload_to_s3(filepath, key):
    bucket = s3_bucket()
    bucket.upload_file(Filename=filepath, Key=key)
