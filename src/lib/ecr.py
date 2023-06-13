import boto3

class ECR(object):
  ''' interface with AWS ECR '''

  def __init__(self):
    self.ecr = boto3.client('ecr')

  def get_repos(self):
    repos = []
    res = self.ecr.describe_repositories()
    repos += res['repositories']
    while 'nextToken' in res:
      res = self.ecr.describe_repositories(nextToken=res['nextToken'])
      repos += res['repositories']
    return repos

  def get_repo_tags(self, arn):
    tags = self.ecr.list_tags_for_resource(resourceArn=arn)
    return tags
