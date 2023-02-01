import os
import subprocess

from enum import Enum

class Drift(Enum):
  ''' enumerates all possible terraform drift detction results '''
  NODRIFT = 0
  DRIFT = 1
  UNKNOWN = 2

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
