import argparse
import logging
import os

import migrate_config_secrets.context

from migrate_config_secrets.migrate import migrate_config_secrets
from lib.logging import setup_logging


def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument(
    'artsy_env',
    choices=['staging', 'production'],
    help='the artsy environment'
  )
  parser.add_argument(
    'artsy_project',
    help='the artsy project to work on'
  )
  parser.add_argument(
    'repos_base_dir',
    help='directory where all the project github repos are stored locally'
  )
  parser.add_argument(
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  parser.add_argument(
    '--secrets_list',
    default=None,
    help="file with list of sensitive config vars of the project, if no such list, you will be prompted for each existent config var and asked whether it's sensitive or not"
  )
  return parser.parse_args()

if __name__ == "__main__":

  args = parse_args()
  artsy_env, artsy_project, repos_base_dir, loglevel, secrets_list = (
    args.artsy_env,
    args.artsy_project,
    args.repos_base_dir,
    args.loglevel,
    args.secrets_list
  )

  setup_logging(eval('logging.' + loglevel))

  migrate_config_secrets(artsy_env, artsy_project, secrets_list, repos_base_dir)
