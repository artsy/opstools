from boto3 import client as boto3_client

class S3Interface:
  ''' interface with AWS S3 '''

  def __init__(self):
    self._s3 = boto3_client('s3')

  def put_file(self, source_file, bucket, key):
    with open(source_file, 'rb') as data:
      self._s3.upload_fileobj(data, bucket, key)
