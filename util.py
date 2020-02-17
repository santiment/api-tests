import boto3
from constants import ACCESS_KEY, ACCESS_SECRET, BUCKET_NAME

def s3_bucket():
    session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)
    s3 = session.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)
    return bucket
