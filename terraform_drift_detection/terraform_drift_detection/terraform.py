import glob
import os

from terraform_drift_detection.util import Drift, run_cmd

def check_dir(dirx):
  init_cmd = 'terraform init'
  plan_cmd = 'terraform plan -detailed-exitcode'
  output = run_cmd(init_cmd, dirx)
  if output.returncode != 0:
    return Drift.UNKNOWN
  output = run_cmd(plan_cmd, dirx)
  if output.returncode == 0:
    return Drift.NODRIFT
  elif output.returncode == 2:
    return Drift.DRIFT
  else:
    return Drift.UNKNOWN

def check_repo(repo, basedir):
  repo_dir = os.path.join(basedir, repo)
  clone_cmd = 'git clone git@github.com:artsy/' + repo + '.git'
  output = run_cmd(clone_cmd, basedir)
  if output.returncode != 0:
    return [Drift.UNKNOWN]
  results = []
  tf_dirs = find_tf_dirs(repo_dir)
  for tf_dir in tf_dirs:
    results += [check_dir(tf_dir)]
  return results

def find_tf_dirs(dirx):
  ''' return list of sub dirs that have .tf files '''
  globstr = dirx + '/**/*.tf'
  tf_files = [
    path for path in glob.glob(globstr, recursive=True)
    if os.path.isfile(path)
  ]
  tf_dirs = [os.path.dirname(path) for path in tf_files]
  return sorted(list(set(tf_dirs)))
