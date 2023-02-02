import os
import subprocess

from enum import Enum

class Drift(Enum):
  ''' enumerate terraform drift detection results '''
  NODRIFT = 0
  DRIFT = 1
  UNKNOWN = 2

def getenv():
  ''' get env '''
  repos = os.getenv('REPO_NAMES', default='')
  github_key = os.getenv('GITHUB_KEY', default='')
  return repos.split(','), github_key

def run_cmd(cmd, dirx):
  ''' run command in dir and return output '''
  os.chdir(dirx)
  print('INFO: running "%s" command in "%s" directory.' %(cmd, dirx))
  output = subprocess.run(cmd, shell=True, text=True, capture_output=True)
  print('INFO: "%s" command exited with code "%s".' %(cmd, output.returncode))
  return output

def validate(repo_names, github_key):
  ''' validate input '''
  valid = []
  valid += [validate_repo_names(repo_names)]
  return not False in valid

def validate_repo_name(name):
  ''' validate repo name '''
  valid = len(name) > 0
  return valid

def validate_repo_names(names):
  ''' validate repo names '''
  valid = []
  valid += [len(names) > 0]
  valid = valid + [validate_repo_name(name) for name in names]
  return not False in valid
