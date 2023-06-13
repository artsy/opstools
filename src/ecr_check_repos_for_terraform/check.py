#!/usr/bin/env python

import logging

# initialize the app
from ecr_check_repos_for_terraform.config import config

from ecr_check_repos_for_terraform.check_repos import (
  check
)

if __name__ == "__main__":

  logging.info('Checking ECR for repositories that are not managed by Terraform and are not for testing.')
  repos = check()
  if len(repos) > 0:
    logging.info(f"Found ECR repos that are non-terraform-managed and not-for-testing: {repos}")
