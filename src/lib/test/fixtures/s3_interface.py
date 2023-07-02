import datetime
import pytest

from dateutil.tz import tzutc

from lib.s3_interface import S3Interface

@pytest.fixture
def s3_interface_obj(mocker, mock_s3_client):
  mocker.patch('lib.s3_interface.S3Interface.__init__', return_value=None)
  obj = S3Interface()
  obj._s3 = mock_s3_client
  return obj

@pytest.fixture
def mock_s3_client():
  class MockS3Client:
    def __init__(self):
      self.foo = 'bar'
    def delete_object(self, Bucket, Key):
      pass
    def list_objects(self, Bucket, Prefix):
      return 'objects'
    def upload_fileobj(data, bucket, key):
      pass
  return MockS3Client()

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
        'ETag': '"123"',
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
