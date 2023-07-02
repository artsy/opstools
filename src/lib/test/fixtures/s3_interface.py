import datetime
import pytest

from dateutil.tz import tzutc

@pytest.fixture
def mock_s3_interface(mock_s3_list_objects_result):
  class MockS3Interface:
    def __init__(self):
      pass
    def put_file(self, file, bucket, key):
      pass
    def list_objects(self, bucket, prefix):
      return mock_s3_list_objects_result
    def delete_object(self, bucket, key):
      pass
  return MockS3Interface()

@pytest.fixture
def mock_s3_list_objects_result():
  obj = {
    'ResponseMetadata': {
      'RequestId': '123',
      'HostId': '123',
      'HTTPStatusCode': 200,
      'HTTPHeaders': {
        'x-amz-id-2': '123',
        'x-amz-request-id': '123',
        'date': 'Sun, 02 Jul 2023 00:18:26 GMT',
        'x-amz-bucket-region': 'us-east-1',
        'content-type': 'application/xml',
        'transfer-encoding': 'chunked',
        'server': 'AmazonS3'
      },
      'RetryAttempts': 0
    },
    'IsTruncated': False,
    'Marker': '',
    'Contents': [
      {
        'Key': 'fooprefix/fooapp/fooenv/2023-07-01_00:22:49.920207+00:00.tar.gz',
        'LastModified': datetime.datetime(2023, 7, 1, 0, 22, 51, tzinfo=tzutc()),
        'ETag': '"e48f2b44f3c684f8a3fe97501f1fa8b3"',
        'Size': 123,
        'StorageClass': 'STANDARD',
        'Owner': {
          'DisplayName': 'bob',
          'ID': '123'
        }
      }
    ],
    'Name': 'foobucket',
    'Prefix': 'a/b/staging',
    'MaxKeys': 1000,
    'EncodingType': 'url'
  }
  return obj
