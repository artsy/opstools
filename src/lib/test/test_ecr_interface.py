import boto3

from lib.ecr_interface import ECRInterface
from lib.test.fixtures.ecr_interface import (
  mock_boto3_client,
  mock_ecr_describe_repositories_result, # indirect
  mock_ecr_list_tags_for_resource_result # indirect
)

def describe_ecr_interface():
  def describe_get_repos():
    def it_gets(mocker, mock_boto3_client):
      mocker.patch(
        'lib.ecr_interface.boto3.client',
        return_value=mock_boto3_client
      )
      ecr_interface = ECRInterface()
      repos = ecr_interface.get_repos()
      assert len(repos) == 2
      assert repos[0]['repositoryName'] == 'foo1'
  def describe_get_repo_tags():
    def it_gets(mocker, mock_boto3_client):
      mocker.patch(
        'lib.ecr_interface.boto3.client',
        return_value=mock_boto3_client
      )
      ecr_interface = ECRInterface()
      res = ecr_interface.get_repo_tags('foo1')
      assert res['tags'][0] == {
        'Key': 'env', 'Value': 'test'
      }
