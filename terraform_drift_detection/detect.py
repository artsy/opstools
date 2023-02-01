#!/usr/bin/env python

# Requirements:
#
# - AWS credentials for Terraform AWS Provider.
#   https://registry.terraform.io/providers/hashicorp/aws/latest/docs
#
# - SSH key for cloning Github repos.
#
# - Repo list.

import os
import tempfile

from terraform_drift_detection.git import clone_repo
from terraform_drift_detection.terraform import find_tf_dirs, tf_in_repo_dir
from terraform_drift_detection.util import abort_on_nonzero_exit, getenv, run_cmd

######
# main
######

repos, github_key = getenv()

with tempfile.TemporaryDirectory() as tmpdir:
  for repo in repos:
    print('INFO: checking repo: %s' %repo)
    clone_repo(repo, tmpdir)
    repo_dir = os.path.join(tmpdir, repo)
    tf_dirs = find_tf_dirs(repo_dir)
    for tf_dir in tf_dirs:
      tf_in_repo_dir(tf_dir)
