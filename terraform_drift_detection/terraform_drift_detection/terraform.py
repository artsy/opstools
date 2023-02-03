import glob
import logging
import os
import tempfile

from terraform_drift_detection.util import Drift, run_cmd

def check_dir(dirx):
  ''' return drift detection result for dir '''
  init_cmd = 'terraform init'
  output = run_cmd(init_cmd, dirx)
  if output.returncode != 0:
    return Drift.UNKNOWN
  plan_cmd = 'terraform plan -detailed-exitcode'
  output = run_cmd(plan_cmd, dirx)
  if output.returncode == 0:
    return Drift.NODRIFT
  elif output.returncode == 2:
    return Drift.DRIFT
  else:
    return Drift.UNKNOWN

def check_repo(repo, basedir, github_token):
  ''' return drift detection result for repo '''
  clone_cmd = 'git clone https://github:' + github_token + '@github.com/artsy/' + repo + '.git'
  output = run_cmd(clone_cmd, basedir)
  if output.returncode != 0:
    return [Drift.UNKNOWN]
  repo_dir = os.path.join(basedir, repo)
  tf_dirs = find_tf_dirs(repo_dir)
  results = [check_dir(tf_dir) for tf_dir in tf_dirs]
  return results

def check_repos(repo_names, github_token):
  ''' return drift detection result for repos '''
  results = []
  with tempfile.TemporaryDirectory() as tmpdir:
    for repo in repo_names:
      results += check_repo(repo, tmpdir, github_token)
  return results

def find_tf_dirs(dirx):
  ''' return sub dirs that house terraform plans '''
  globstr = dirx + '/**/*.tf'
  tf_files = [
    path for path in glob.glob(globstr, recursive=True)
    if os.path.isfile(path)
  ]
  tf_dirs = [os.path.dirname(path) for path in tf_files]
  return sorted(list(set(tf_dirs)))
