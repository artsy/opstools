import argparse
import logging
import os

import migrate_config_secrets.context

from migrate_config_secrets.migrate import migrate_config_secrets
from lib.logging import setup_logging


def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description=(
      'Migrate sensitive configs of an Artsy project ' +
      'from Kubernetes configmap to Hashicorp Vault'
    )
  )
  parser.add_argument(
    'artsy_env',
    choices=['staging', 'production'],
    help='artsy environment'
  )
  parser.add_argument(
    'artsy_project',
    help='artsy project'
  )
  parser.add_argument(
    'repos_base_dir',
    help='directory where all the Github repos are stored locally'
  )
  parser.add_argument(
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  parser.add_argument(
    '--list',
    default=None,
    help=(
      'file containing a list of the sensitive configs, ' +
      'if not provided, you will be prompted ' +
      'for each config var of the project ' +
      'and asked whether it is sensitive or not'
    )
  )
  return parser.parse_args()

if __name__ == "__main__":

  args = parse_args()
  artsy_env, artsy_project, repos_base_dir, loglevel, list = (
    args.artsy_env,
    args.artsy_project,
    args.repos_base_dir,
    args.loglevel,
    args.list
  )

  setup_logging(eval('logging.' + loglevel))

  migrate_config_secrets(artsy_env, artsy_project, list, repos_base_dir)
