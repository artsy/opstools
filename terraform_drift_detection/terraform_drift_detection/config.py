import os

from cerberus import Validator

class AppConfig:
  ''' get env config and validate them '''
  def __init__(self, env):
    self.github_token = env.get('GITHUB_TOKEN', '')
    repo_names = env.get('REPO_NAMES', '')
    self.repos = repo_names.split(',')
    validate(self.github_token, repo_names, self.repos)

class AppConfigError(Exception):
  pass

def validate(github_token, repo_names, repos):
  ''' validate input data '''
  validator = Validator()
  schema = {
    'github_token': {'type': 'string', 'empty': False},
    'repo_names': {'type': 'string', 'empty': False},
    'repos': {'type': 'list', 'empty': False, 'schema': {'type': 'string', 'empty': False}}
  }
  document = {
    'github_token': github_token,
    'repo_names': repo_names,
    'repos': repos
  }
  if not validator.validate(document, schema):
    raise AppConfigError('Error: Env vars are missing or invalid.')

# import this from other modules in order to instantiate
config = AppConfig(os.environ)
