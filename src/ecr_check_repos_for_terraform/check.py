import logging

# initialize the app
from ecr_check_repos_for_terraform.config import config

from ecr_check_repos_for_terraform.check_repos import check

if __name__ == "__main__":

  logging.info(
    'Checking ECR for repositories that perhaps should be added to Terraform...'
  )
  repos = check()
  if len(repos) > 0:
    logging.info(f"Repositories found: {repos}")
    exit(1)
  else:
    logging.info("None found.")
