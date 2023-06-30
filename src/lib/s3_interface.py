import logging

from boto3 import client as boto3_client

class S3Interface:
  ''' interface with AWS S3 '''
  def __init__(self):
    self._s3 = boto3_client('s3')

  def delete_object(self, bucket, key):
    ''' delete the given key in given bucket '''
    logging.debug(
      f"S3Interface: deleting s3://{bucket}/{key}"
    )
    self._s3.delete_object(Bucket=bucket, Key=key)

  def list_objects(self, bucket, prefix):
    ''' list objects under the given prefix in the given bucket '''
    logging.debug(
      f"S3Interface: listing objects in s3://{bucket}/{prefix}/"
    )
    # returns up to 1000 objects by default
    objects = self._s3.list_objects(Bucket=bucket, Prefix=prefix)
    return objects

  def put_file(self, source_file, bucket, key):
    ''' upload source_file to the given s3 bucket and key '''
    with open(source_file, 'rb') as data:
      self._s3.upload_fileobj(data, bucket, key)
