import os

from cerberus import Validator

class AppConfig:
  ''' get env config and validate them '''
  def __init__(self, env):
    self.github_token = env.get('GITHUB_TOKEN', '')
    reposdirs = env.get('REPOSDIRS', '')
    self.repos_dirs = parse_reposdirs(reposdirs)

    if not validate(self.github_token, reposdirs, self.repos_dirs):
      raise AppConfigError('Error: Env vars are missing or invalid.')

class AppConfigError(Exception):
  pass

def parse_reposdirs(reposdirs):
  ''' given 'repo1:dir1,repo1:dir2,repo2:dir1', return {'repo1': ['dir1', 'dir2'], 'repo2': ['dir1']} '''
  repos_dirs = {}
  for repodir in reposdirs.split(','):
    repo, dir = repodir.split(':')
    repos_dirs[repo] = repos_dirs.get(repo, []) + [dir]
  return repos_dirs

def validate(github_token, reposdirs, repos_dirs):
  ''' validate input data '''
  validator = Validator()
  schema = {
    'github_token': {'type': 'string', 'empty': False},
    'reposdirs': {'type': 'string', 'empty': False},
    'repos_dirs': {
      'type': 'dict',
      'empty': False,
      'keysrules': {'type': 'string', 'empty': False},
      'valuesrules': {
        'type': 'list',
        'empty': False,
        'schema': {
          'type': 'string', 'empty': False
        }
      }
    }
  }
  document = {
    'github_token': github_token,
    'reposdirs': reposdirs,
    'repos_dirs': repos_dirs
  }
  return validator.validate(document, schema)

# import this from other modules in order to instantiate
config = AppConfig(os.environ)
