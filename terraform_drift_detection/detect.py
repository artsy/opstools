#!/usr/bin/env python

import logging

from terraform_drift_detection.terraform import check_repos
from terraform_drift_detection.util import Drift, getenv, setup_logging, validate

setup_logging()
repo_names, github_token = getenv()

if validate(repo_names, github_token):
  results = check_repos(repo_names, github_token)
  if Drift.DRIFT in results:
    logging.error('Drift detected.')
    exit(1)
else:
  logging.info('Input is invalid.')
