import logging
import os
import re
import subprocess

from enum import Enum

class Drift(Enum):
  ''' enumerate terraform drift detection results '''
  NODRIFT = 0
  DRIFT = 1
  UNKNOWN = 2

class FilterOutSensitiveInfoFormatter(logging.Formatter):
  ''' filter out sensitive info from logs '''
  @staticmethod
  def _filter(log):
    try:
      # https://<sensitive>@foo.com... urls
      return re.sub(r':\/\/(.*?)\@', r'://<FILTERED>@', log)
    except:
      # exception's output includes the app log that triggered the exception.
      # since the app log may contain sensitive data, silence the exception.
      print('Error: FilterOutSensitiveInfoFormatter._filter() raised an exception.')
      exit(1)

  def format(self, record):
    formatted_log = logging.Formatter.format(self, record)
    return self._filter(formatted_log)

def getenv():
  ''' get env '''
  repos = os.getenv('REPO_NAMES', default='')
  github_token = os.getenv('GITHUB_TOKEN', default='')
  return repos.split(','), github_token

def run_cmd(cmd, dirx):
  ''' run command in dir and return output '''
  os.chdir(dirx)
  logging.info('running "%s" command in "%s" directory.', cmd, dirx)
  output = subprocess.run(cmd, shell=True, text=True, capture_output=True)
  logging.info('"%s" command exited with code "%s".', cmd, output.returncode)
  return output

def setup_logging():
  logging.basicConfig(level=logging.INFO)
  format = '%(levelname)s: %(message)s'
  for handler in logging.root.handlers:
     handler.setFormatter(FilterOutSensitiveInfoFormatter(format))

def validate(repo_names, github_token):
  ''' validate input '''
  valid = []
  valid += [validate_repo_names(repo_names)]
  valid += [len(github_token) > 0]
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
