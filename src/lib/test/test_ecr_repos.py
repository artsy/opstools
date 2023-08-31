from lib.ecr_repos import ECRRepo, ECRRepos

from lib.test.fixtures.ecr_interface import (
  mock_ecr_client, # indirect
  mock_ecr_describe_repositories_result,
  mock_ecr_interface,
  mock_ecr_list_tags_for_resource_result
)

def describe_ecr_repo():
  def describe_instantiation():
    def it_instantiates(
      mock_ecr_describe_repositories_result,
      mock_ecr_list_tags_for_resource_result
    ):
      repo_infos = mock_ecr_describe_repositories_result
      repo1_info = repo_infos['repositories'][0]
      res = mock_ecr_list_tags_for_resource_result
      repo1_tags = res['tags']
      ecr_repo = ECRRepo(repo1_info, repo1_tags)
      assert ecr_repo.arn == repo1_info['repositoryArn']
      assert ecr_repo.info == repo1_info
      assert ecr_repo.name == repo1_info['repositoryName']
      assert ecr_repo.tags == repo1_tags

def describe_ecr_repos():
  def describe_instantiation():
    def it_instantiates(mock_ecr_interface):
      ecr_repos = ECRRepos(mock_ecr_interface)
      repo1 = ecr_repos._repos[0]
      assert len(ecr_repos._repos) == 3
      assert isinstance(repo1, ECRRepo)
  def describe_all_repos():
    def it_returns_all_repos(mock_ecr_interface):
      ecr_repos = ECRRepos(mock_ecr_interface)
      assert set(ecr_repos.all_repos()) == set(['foo1', 'foo2', 'bar1'])
  def describe_repos_with_name():
    def partial_match():
      def it_matches(mock_ecr_interface):
        ecr_repos = ECRRepos(mock_ecr_interface)
        repos = ecr_repos.repos_with_name('foo')
        assert set(repos) == set(['foo1', 'foo2'])
      def it_does_not_match(mock_ecr_interface):
        ecr_repos = ECRRepos(mock_ecr_interface)
        repos = ecr_repos.repos_with_name('fin')
        assert repos == []
    def exact_match():
      def it_matches(mock_ecr_interface):
        ecr_repos = ECRRepos(mock_ecr_interface)
        repos = ecr_repos.repos_with_name('foo1')
        assert repos == ['foo1']
      def it_does_not_match(mock_ecr_interface):
        ecr_repos = ECRRepos(mock_ecr_interface)
        repos = ecr_repos.repos_with_name('foo')
        assert repos == []
  def describe_repos_wit_tag():
    def it_gets_correct_repos(mock_ecr_interface):
      ecr_repos = ECRRepos(mock_ecr_interface)
      tag = {'Key': 'env', 'Value': 'test'}
      repos = ecr_repos.repos_with_tag(tag)
      assert len(repos) == 1
      assert repos[0] == 'foo1'
