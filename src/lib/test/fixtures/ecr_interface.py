import datetime
import pytest

from dateutil.tz import tzlocal

@pytest.fixture
def mock_boto3_client(
  mock_ecr_describe_repositories_result,
  mock_ecr_list_tags_for_resource_result
):
  class MockECRClient():
    def __init__(self):
      pass
    def describe_repositories(self, *args):
      return mock_ecr_describe_repositories_result
    def list_tags_for_resource(self, **kwargs):
      return mock_ecr_list_tags_for_resource_result
  return MockECRClient()

@pytest.fixture
def mock_ecr_describe_repositories_result():
  obj = {
    'repositories': [
      {
        'repositoryArn': 'arn:aws:ecr:us-east-1:123:repository/foo1',
        'registryId': '123',
        'repositoryName': 'foo1',
        'repositoryUri': '123.dkr.ecr.us-east-1.amazonaws.com/foo1',
        'createdAt': datetime.datetime(2023, 6, 13, 16, 50, 21, tzinfo=tzlocal()),
        'imageTagMutability': 'MUTABLE',
        'imageScanningConfiguration': {'scanOnPush': False},
        'encryptionConfiguration': {'encryptionType': 'AES256'}
      },
      {
        'repositoryArn': 'arn:aws:ecr:us-east-1:123:repository/foo2',
        'registryId': '123',
        'repositoryName': 'foo2',
        'repositoryUri': '123.dkr.ecr.us-east-1.amazonaws.com/foo2',
        'createdAt': datetime.datetime(2023, 6, 13, 16, 50, 21, tzinfo=tzlocal()),
        'imageTagMutability': 'MUTABLE',
        'imageScanningConfiguration': {'scanOnPush': False},
        'encryptionConfiguration': {'encryptionType': 'AES256'}
      }
    ]
  }
  return obj

@pytest.fixture
def mock_ecr_list_tags_for_resource_result():
  obj = {
    'tags': [
      {'Key': 'env', 'Value': 'test'}
    ],
    'ResponseMetadata': {
      'RequestId': 'a9918a87-e51e-4ec0-8c95-34110ae253d1',
      'HTTPStatusCode': 200,
      'HTTPHeaders': {
        'x-amzn-requestid': 'a9918a87-e51e-4ec0-8c95-34110ae253d1',
        'date': 'Wed, 14 Jun 2023 18:31:40 GMT',
        'content-type': 'application/x-amz-json-1.1',
        'content-length': '39'
      },
      'RetryAttempts': 0
    }
  }
  return obj
