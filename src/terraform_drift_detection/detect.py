import argparse
import logging
import os

from cerberus import Validator

import terraform_drift_detection.context

from terraform_drift_detection.terraform import (
  check_repos,
  Drift
)
from lib.logging import setup_sensitive_logging
from lib.util import parse_string_of_key_value_pairs


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

def parse_env():
  ''' parse env vars '''
  github_token = os.environ.get('GITHUB_TOKEN', '')
  reposdirs = os.environ.get('REPOSDIRS', '')
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


if __name__ == "__main__":

  args = parse_args()
  loglevel = args.loglevel

  setup_sensitive_logging(eval('logging.' + loglevel))

  github_token, reposdirs = parse_env()

  repos_dirs = parse_string_of_key_value_pairs(reposdirs)
  validate(github_token, reposdirs, repos_dirs)

  if Drift.DRIFT in check_repos(github_token, repos_dirs):
    logging.error('Drift detected.')
    exit(1)
