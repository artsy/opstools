import lib.test.fixtures.ecr_interface

from lib.ecr_interface import ECRInterface
from lib.test.fixtures.ecr_interface import (
  mock_ecr_client,
  mock_ecr_describe_repositories_result, # indirect
  mock_ecr_list_tags_for_resource_result, # indirect
)

def describe_ecr_interface():
  def describe_instantiation():
    def it_instantiates(mocker, mock_ecr_client):
      mocker.patch(
        'lib.ecr_interface.boto3_client',
        return_value=mock_ecr_client
      )
      spy = mocker.spy(lib.ecr_interface, 'boto3_client')
      ecr_interface = ECRInterface()
      spy.assert_has_calls([mocker.call('ecr')])
  def describe_get_repos():
    def it_gets(mocker, mock_ecr_client):
      mocker.patch(
        'lib.ecr_interface.boto3_client',
        return_value=mock_ecr_client
      )
      ecr_interface = ECRInterface()
      repos = ecr_interface.get_repos()
      assert len(repos) == 2
      assert repos[0]['repositoryName'] == 'foo1'
  def describe_get_repo_tags():
    def it_gets(mocker, mock_ecr_client):
      mocker.patch(
        'lib.ecr_interface.boto3_client',
        return_value=mock_ecr_client
      )
      ecr_interface = ECRInterface()
      arn = 'arn:aws:ecr:us-east-1:123:repository/foo1'
      res = ecr_interface.get_repo_tags(arn)
      assert res['tags'][0] == {
        'Key': 'env', 'Value': 'test'
      }
