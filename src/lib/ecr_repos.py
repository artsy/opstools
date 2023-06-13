import logging

class EcrRepo():
  ''' manage 1 ECR repository's data '''
  def __init__(self, repo_info, tags):
    self.info = repo_info
    self.name = repo_info['repositoryName']
    self.arn = repo_info['repositoryArn']
    self.tags = tags

class EcrRepos():
  ''' manage ECR repositories data '''
  def __init__(self, ecr_client):
    self._ecr_client = ecr_client
    repos_info = ecr_client.get_repos()
    self._repo_objs = []
    for repo_info in repos_info:
      repo_name = repo_info['repositoryName']
      repo_arn = repo_info['repositoryArn']
      res = ecr_client.get_repo_tags(repo_arn)
      tags = res['tags']
      repo_obj = EcrRepo(repo_info, tags)
      self._repo_objs += [repo_obj]

  def all_repos(self):
    ''' return names of all repos, sorted '''
    return sorted(
      [obj.name for obj in self._repo_objs]
    )

  def repos_with_tag(self, tag):
    ''' return names of repos that have the specified tag '''
    repos = []
    for obj in self._repo_objs:
      if tag in obj.tags:
        repos += [obj.name]
    return repos

  def get_repo(self, repo_name):
    ''' return EcrRepo object whose name matches repo_name '''
    for obj in self._repo_objs:
      if obj.name == repo_name:
        return obj

  def get_repo_info(self, repo_name):
    info = None
    for obj in self._repo_objs:
      if obj.name == repo_name:
        info = obj.info
        break
    return info

  def get_repo_tags(self, repo_name):
    tags = None
    for obj in self._repo_objs:
      if obj.name == repo_name:
        tags = obj.tags
    return tags
