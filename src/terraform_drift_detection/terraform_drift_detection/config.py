import argparse
import logging
import os

from cerberus import Validator

import terraform_drift_detection.context

from lib.logging import setup_sensitive_logging
from lib.util import parse_string_of_key_value_pairs

class AppConfig:
  def __init__(self, cmdline_args, env):
    ''' set app-wide configs and initialize the app '''
    loglevel = cmdline_args.loglevel
    self.github_token, reposdirs = env
    self.repos_dirs = parse_string_of_key_value_pairs(reposdirs)
    validate(self.github_token, reposdirs, self.repos_dirs)
    self._init_app(loglevel)

  def _init_app(self, loglevel):
    ''' initialize the app '''
    # initialize logging
    setup_sensitive_logging(eval('logging.' + loglevel))

def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument(
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  return parser.parse_args()

def parse_env(env):
  ''' parse env vars '''
  github_token = env.get('GITHUB_TOKEN', '')
  reposdirs = env.get('REPOSDIRS', '')
  return github_token, reposdirs

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
  if not validator.validate(document, schema):
    raise Exception('Invalid config.')

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args(), parse_env(os.environ))
