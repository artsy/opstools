import logging

from boto3 import client as boto3_client

class S3Interface:
  ''' interface with AWS S3 '''

  def __init__(self):
    self._s3 = boto3_client('s3')

  def delete_object(self, bucket, key):
    ''' delete object in bucket key '''
    logging.debug(
      f"S3Interface: deleting s3://{bucket}/{key}"
    )
    self._s3.delete_object(Bucket=bucket, Key=key)

  def list_objects(self, bucket, prefix):
    ''' list objects in bucket prefix '''
    logging.debug(f"S3Interface: listing objects in {bucket} bucket {prefix} prefix")
    return self._s3.list_objects(Bucket=bucket, Prefix=prefix)

  def put_file(self, source_file, bucket, key):
    ''' copy source_file to s3 bucket key '''
    with open(source_file, 'rb') as data:
      self._s3.upload_fileobj(data, bucket, key)
