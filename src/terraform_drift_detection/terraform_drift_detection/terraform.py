import logging
import os
import tempfile

from enum import Enum

import terraform_drift_detection.context

from lib.util import run_cmd, search_dirs_by_suffix
from terraform_drift_detection.config import config

class Drift(Enum):
  ''' enumerate terraform drift detection results '''
  NODRIFT = 0
  DRIFT = 1
  UNKNOWN = 2

def check_dir(dirx):
  ''' return drift detection result for a dir '''
  tf_dirs = search_dirs_by_suffix(dirx, 'tf')
  results = [check_tf_dir(tf_dir) for tf_dir in tf_dirs]
  return results

def check_repo(repo, basedir):
  ''' return drift detection result for repo '''
  clone_cmd = (
    'git clone https://github:' +
    config.github_token +
    '@github.com/artsy/' + repo + '.git'
  )
  output = run_cmd(clone_cmd, basedir)
  if output.returncode != 0:
    return [Drift.UNKNOWN]
  repo_dir = os.path.join(basedir, repo)
  results = []
  for dirx in config.repos_dirs[repo]:
    results += check_dir(os.path.join(repo_dir, dirx))
  return results

def check_repos():
  ''' return drift detection result for repos '''
  results = []
  with tempfile.TemporaryDirectory() as tmpdir:
    for repo in list(config.repos_dirs.keys()):
      results += check_repo(repo, tmpdir)
  return results

def check_tf_dir(tf_dir):
  ''' return drift detection result for a terraform dir '''
  init_cmd = 'terraform init'
  output = run_cmd(init_cmd, tf_dir)
  if output.returncode != 0:
    return Drift.UNKNOWN
  plan_cmd = 'terraform plan -detailed-exitcode'
  output = run_cmd(plan_cmd, tf_dir)
  if output.returncode == 0:
    return Drift.NODRIFT
  elif output.returncode == 2:
    log_the_drift(output.stdout)
    return Drift.DRIFT
  else:
    return Drift.UNKNOWN

def log_the_drift(tf_output):
  ''' log resources mentioned in terraform plan output showing changes '''
  # the lines marked with '#', example:
  # '# aws_instance.serverx will be updated in-place'
  for line in tf_output.split('\n'):
    if '# ' in line: logging.info(line)
