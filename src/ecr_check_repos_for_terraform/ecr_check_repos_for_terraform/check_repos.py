import ecr_check_repos_for_terraform.context

from lib.ecr_interface import ECRInterface
from lib.ecr_repos import ECRRepos
from lib.util import list_subtract

def check():
  '''
  return names of ECR repositories that:
  - do not have a "managed_by: terraform" tag
  - do not have an "env: test" tag
  - do not have 'test' in their names
  '''
  ecr_interface = ECRInterface()
  ecr_repos = ECRRepos(ecr_interface)
  all_repos = ecr_repos.all_repos()

  tag = {'Key': 'managed_by', 'Value': 'terraform'}
  terraform_managed_repos = ecr_repos.repos_with_tag(tag)

  tag = {'Key': 'env', 'Value': 'test'}
  repos_tagged_test = ecr_repos.repos_with_tag(tag)

  repos_named_test = ecr_repos.repos_with_name('test')

  return list_subtract(
    all_repos,
    terraform_managed_repos,
    repos_tagged_test,
    repos_named_test
  )
