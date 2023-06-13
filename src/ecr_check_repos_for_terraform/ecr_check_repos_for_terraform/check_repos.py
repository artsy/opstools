import logging

import ecr_check_repos_for_terraform.context

from lib.ecr import ECR
from lib.ecr_repos import EcrRepos
from lib.util import list_subtract

def check():
  ''' check for ecr repositories that should be managed by terraform '''
  ecr_client = ECR()
  repos_obj = EcrRepos(ecr_client)
  all_repos = repos_obj.all_repos()
  tag = {'Key': 'managed_by', 'Value': 'terraform'}
  terraform_managed_repos = repos_obj.repos_with_tag(tag)
  tag = {'Key': 'env', 'Value': 'test'}
  test_repos = repos_obj.repos_with_tag(tag)
  non_terraform_managed_repos = list_subtract(all_repos, terraform_managed_repos)
  return list_subtract(non_terraform_managed_repos, test_repos)
