from boto3 import client as boto3_client

class ECRInterface():
  ''' interface with AWS ECR '''

  def __init__(self):
    self._ecr = boto3_client('ecr')

  def get_repos(self):
    repos = []
    res = self._ecr.describe_repositories()
    repos += res['repositories']
    while 'nextToken' in res:
      res = self._ecr.describe_repositories(
        nextToken=res['nextToken']
      )
      repos += res['repositories']
    return repos

  def get_repo_tags(self, arn):
    return self._ecr.list_tags_for_resource(
      resourceArn=arn
    )
