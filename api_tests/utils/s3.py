import s3fs
from ..constants import S3_ACCESS_KEY, S3_ACCESS_SECRET, S3_BUCKET_NAME

fs = s3fs.S3FileSystem(key=S3_ACCESS_KEY, secret=S3_ACCESS_SECRET)

def s3_list_files():
    return fs.ls(S3_BUCKET_NAME)

def upload_to_s3(filepath, key):
    fs.put(filepath, full_key_path(key))

def set_json_content_type(key):
    set_content_type(key, 'application/json')

def set_html_content_type(key):
    set_content_type(key, 'text/html')

def set_content_type(key, content_type):
    fs.setxattr(full_key_path(key), copy_kwargs={'ContentType': content_type})

def s3_read_file_content(filename):
    return fs.cat(filename)

def full_key_path(key):
    return f"{S3_BUCKET_NAME}/{key}"
