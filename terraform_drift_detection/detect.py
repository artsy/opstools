#!/usr/bin/env python

from terraform_drift_detection.terraform import check_repos
from terraform_drift_detection.util import Drift, getenv, validate

repo_names, github_key = getenv()

if validate(repo_names, github_key):
  results = check_repos(repo_names)
  if Drift.DRIFT in results:
    print('Error: Drift detected.')
    exit(1)
else:
  print('INFO: input is invalid.')
  exit(0)
