import s3fs
from constants import S3_ACCESS_KEY, S3_ACCESS_SECRET, S3_BUCKET_NAME

fs = s3fs.S3FileSystem(key=S3_ACCESS_KEY, secret=S3_ACCESS_SECRET)

def s3_list_files():
    return fs.ls(S3_BUCKET_NAME)

def upload_to_s3(filepath, key):
    fs.put(filepath, f"{S3_BUCKET_NAME}/{key}")
