import datetime
import pytest

from dateutil.tz import tzlocal

from lib.ecr_interface import ECRInterface

@pytest.fixture
def ecr_interface_object(mock_ecr_client, mocker):
  mocker.patch(
    'lib.ecr_interface.boto3_client',
    return_value=mock_ecr_client
  )
  ecr_interface = ECRInterface()
  return ecr_interface

@pytest.fixture
def mock_ecr_client(
  mock_ecr_describe_repositories_result,
  mock_ecr_list_tags_for_resource_result
):
  class MockECRClient:
    def __init__(self):
      pass
    def describe_repositories(self, *args):
      return mock_ecr_describe_repositories_result
    def list_tags_for_resource(self, resourceArn):
      if resourceArn == 'arn:aws:ecr:us-east-1:123:repository/foo1':
        return mock_ecr_list_tags_for_resource_result
      else:
        return { 'tags': [] }
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
      },
      {
        'repositoryArn': 'arn:aws:ecr:us-east-1:123:repository/bar1',
        'registryId': '123',
        'repositoryName': 'bar1',
        'repositoryUri': '123.dkr.ecr.us-east-1.amazonaws.com/bar1',
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

@pytest.fixture
def mock_ecr_interface(
  mock_ecr_client,
  mock_ecr_describe_repositories_result,
  mock_ecr_list_tags_for_resource_result
):
  class ECRInterface:
    def __init__(self):
      pass
    def get_repos(self):
      return mock_ecr_describe_repositories_result['repositories']
    def get_repo_tags(self, arn):
      return mock_ecr_client.list_tags_for_resource(resourceArn=arn)
  return ECRInterface()
