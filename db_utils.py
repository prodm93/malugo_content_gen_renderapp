import os
import errno
import boto3
from save_utils import extract_caption
from pyairtable import Table


def upload_to_airtable(table_name, post_object):
    base_id = "app1DYqHEzHFGjD71"
    table = Table(os.environ['AIRTABLE_API_KEY'], base_id, table_name)
    post_and_caption = extract_caption(post_object.content_with_caption)
    record = {
        "Content Type": post_object.content_type,
        "Language": post_object.language,
        "Title": post_object.idea,
        "Content": post_and_caption[0],
        "Caption": post_and_caption[1]
    }
    table.create(record)


def assert_dir_exists(path):
    """
    Checks if directory tree in path exists. If not it created them.
    :param path: the path to check if it exists
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def download_dir(client, bucket, path, target):
    """
    Downloads the given S3 path recursively to the target directory.
    :param client: S3 client to use.
    :param bucket: the name of the bucket to download from
    :param path: The S3 directory to download.
    :param target: the local directory to download the files to.
    """

    # Handle missing / at end of prefix
    if not path.endswith('/'):
        path += '/'

    paginator = client.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket, Prefix=path):
        # Download each file individually
        for key in result['Contents']:
            # Calculate relative path
            rel_path = key['Key'][len(path):]
            # Skip paths ending in /
            if not key['Key'].endswith('/'):
                local_file_path = os.path.join(target, rel_path)
                # Make sure directories exist
                local_file_dir = os.path.dirname(local_file_path)
                assert_dir_exists(local_file_dir)
                client.download_file(bucket, key['Key'], local_file_path)

def get_client():
    # get these values from the corresponding access_key.json file for your iDrive e2 account
    config = {"Endpoint": "s3.filebase.com",
                "Access Key": "E3D9EB8DEAB2E4FED68A",
                "Secret Key": "FA3DS1fL3tRNgD0lrH7CnXAzi0diekhdDwihzjCm"}
    

    client = boto3.client('s3', endpoint_url = "https://{}".format(config["Endpoint"]),
                    aws_access_key_id=config["Access Key"],
                    aws_secret_access_key=config["Secret Key"]
                )
    return client


def filebase_download(bucket, idrive_dir, download_path):
    client = get_client()
    client.download_file(bucket, idrive_dir, download_path)

def filebase_upload(src_path, bucket, upload_dir):
    client = get_client()
    client.upload_file(src_path, bucket, upload_dir)

