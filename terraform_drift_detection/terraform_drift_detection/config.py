import os

class AppConfig:
  def __init__(self, env):
    repo_names = env.get('REPO_NAMES', '')
    self.github_token = env.get('GITHUB_TOKEN', '')
    self.repos = repo_names.split(',')
    if not validate(self.repos, self.github_token):
      raise AppConfigError('Error: Env vars are missing or invalid.')

class AppConfigError(Exception):
    pass

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

config = AppConfig(os.environ)
