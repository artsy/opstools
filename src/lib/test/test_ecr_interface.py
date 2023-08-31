from lib.test.fixtures.ecr_interface import (
  ecr_interface_object,
  mock_ecr_client,
  mock_ecr_describe_repositories_result, # indirect
  mock_ecr_list_tags_for_resource_result, # indirect
)

def describe_ecr_interface():

  def describe_instantiation():
    def it_instantiates(mocker, ecr_interface_object, mock_ecr_client):
      assert ecr_interface_object._ecr is mock_ecr_client

  def describe_get_repos():
    def it_gets(mocker, ecr_interface_object):
      repos = ecr_interface_object.get_repos()
      assert len(repos) == 3
      assert repos[0]['repositoryName'] == 'foo1'

  def describe_get_repo_tags():
    def it_gets(mocker, ecr_interface_object):
      arn = 'arn:aws:ecr:us-east-1:123:repository/foo1'
      res = ecr_interface_object.get_repo_tags(arn)
      assert res['tags'][0] == {
        'Key': 'env', 'Value': 'test'
      }
