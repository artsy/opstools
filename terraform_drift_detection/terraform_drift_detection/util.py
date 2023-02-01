import os
import subprocess

def abort_on_nonzero_exit(cmd, code):
  ''' print error message and exit program '''
  if code != 0:
    print('ERROR: Aborting, because "%s" command exited with code %s.' %(cmd, code))
    exit(code)

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
