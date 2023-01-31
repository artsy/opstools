#!/usr/bin/env python

# Requirements:
#
# - AWS credentials for Terraform AWS Provider.
#   https://registry.terraform.io/providers/hashicorp/aws/latest/docs
#
# - SSH key for cloning Github repos.
#
# - Repo list.

import glob
import os
import subprocess
import tempfile

def abort_on_nonzero_exit(cmd, code):
  ''' print error message and exit program '''
  if code != 0:
    print('ERROR: Aborting, because "%s" command exited with code %s.' %(cmd, code))
    exit(code)

def clone_repo(repo, dirx):
  ''' git clones a repo '''
  cmd = 'git clone git@github.com:artsy/' + repo + '.git'
  output = run_cmd(cmd, dirx)
  abort_on_nonzero_exit(cmd, output.returncode)

def find_tf_dirs(dirx):
  ''' return list of sub dirs that have .tf files '''
  globstr = dirx + '/**/*.tf'
  tf_files = [
    path for path in glob.glob(globstr, recursive=True)
    if os.path.isfile(path)
  ]
  tf_dirs = [os.path.dirname(path) for path in tf_files]
  return list(set(tf_dirs))

def getenv():
  repos = os.getenv('REPOS', default='')
  github_key = os.getenv('GITHUB_KEY', default='')
  return repos.split(','), github_key

def run_cmd(cmd, dirx):
  ''' run command in dir '''
  os.chdir(dirx)
  print('INFO: running "%s" command in "%s" directory.' %(cmd, dirx))
  output = subprocess.run(cmd, shell=True, text=True, capture_output=True)
  return output

def tf_in_repo_dir(dirx):
  ''' run terraform commands in dir '''
  init_cmd = 'terraform init'
  plan_cmd = 'terraform plan -detailed-exitcode'
  output = run_cmd(init_cmd, dirx)
  abort_on_nonzero_exit(init_cmd, output.returncode)
  output = run_cmd(plan_cmd, tf_dir)
  if output.returncode == 0:
    print('INFO: terraform plan suceeded and reported no changes.')
  else:
    print('ERROR: there is possibly drift between tf plans and cloud config.')
    abort_on_nonzero_exit(plan_cmd, output.returncode)

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
