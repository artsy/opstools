import glob
import logging
import os
import tempfile

from terraform_drift_detection.config import config
from terraform_drift_detection.util import Drift, run_cmd

def check_dir(dirx):
  ''' return drift detection result for a dir '''
  tf_dirs = find_tf_dirs(dirx)
  results = [check_tf_dir(tf_dir) for tf_dir in tf_dirs]
  return results

def check_repo(repo, basedir):
  ''' return drift detection result for repo '''
  clone_cmd = 'git clone https://github:' + config.github_token + '@github.com/artsy/' + repo + '.git'
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
    return Drift.DRIFT
  else:
    return Drift.UNKNOWN

def find_tf_dirs(dirx):
  ''' return sub dirs that house terraform plans '''
  globstr = dirx + '/**/*.tf'
  tf_files = [
    path for path in glob.glob(globstr, recursive=True)
    if os.path.isfile(path)
  ]
  tf_dirs = [os.path.dirname(path) for path in tf_files]
  return sorted(list(set(tf_dirs)))
