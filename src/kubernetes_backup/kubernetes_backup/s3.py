import os

import boto3

class S3Interface(object):
  KEY_SUFFIX = '.tar.gz'

  def __init__(self, bucket_name, prefix=''):
    self.client = boto3.client('s3')
    self.bucket_name = bucket_name
    self.bucket_prefix = prefix

  def put_file(self, file_path, key):
    with open(file_path, 'rb') as f:
      self.client.upload_fileobj(f, self.bucket_name, key)

  def backup(self, file_path, backup_name):
    self.put_file(file_path, os.path.join(self.bucket_prefix, backup_name + self.KEY_SUFFIX))
    return os.path.join(self.bucket_prefix, backup_name)
