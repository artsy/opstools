class ECRRepo():
  ''' manage 1 ECR repository's data '''
  def __init__(self, repo_info, tags):
    self.arn = repo_info['repositoryArn']
    self.info = repo_info
    self.name = repo_info['repositoryName']
    self.tags = tags

class ECRRepos():
  ''' manage all ECR repositories' data '''
  def __init__(self, ecr_interface):
    self._ecr_interface = ecr_interface
    repos = ecr_interface.get_repos()
    self._repos = []
    for repo in repos:
      name = repo['repositoryName']
      arn = repo['repositoryArn']
      res = ecr_interface.get_repo_tags(arn)
      tags = res['tags']
      ecr_repo = ECRRepo(repo, tags)
      self._repos += [ecr_repo]

  def all_repos(self):
    ''' return names of all repos, sorted '''
    return sorted(
      [repo.name for repo in self._repos]
    )

  def get_repo(self, repo_name):
    ''' return ECRRepo object whose name matches repo_name '''
    for repo in self._repos:
      if repo.name == repo_name:
        return repo

  def repos_with_tag(self, tag):
    ''' return names of repos that have the specified tag '''
    return sorted([
      repo.name for repo in self._repos
      if tag in repo.tags
    ])
