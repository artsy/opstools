#!/usr/bin/env python

import os
import tempfile

from terraform_drift_detection.util import Drift, getenv

repo_names, github_key = getenv()

with tempfile.TemporaryDirectory() as tmpdir:
  results = []
  for repo in repo_names:
    results += check_repo(repo, tmpdir)
  if Drift.DRIFT in results:
    print('Error: Drift detected')
    exit(1)
