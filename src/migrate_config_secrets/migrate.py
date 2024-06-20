import argparse
import logging
import os

import migrate_config_secrets.context

from migrate_config_secrets.migrate import migrate_config_secrets
from lib.logging import setup_logging
from lib.validations import (
  hostname_agrees_with_artsy_environment
)


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
    '--dry-run',
    action="store_true",
    help=("Dry Run. Won't make any changes.")
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
  vault_host = os.environ.get('VAULT_HOST')
  vault_port = os.environ.get('VAULT_PORT')
  kvv2_mount_point = os.environ.get('VAULT_KVV2_MOUNT_POINT')
  return vault_host, vault_port, kvv2_mount_point

def validate(artsy_env, vault_host, vault_port):
  ''' validate config obtained from env and command line '''
  if not (vault_host and vault_port):
    raise Exception(
      "The following environment variables must be specified: " +
      "VAULT_HOST, " +
      "VAULT_PORT"
    )
  if not hostname_agrees_with_artsy_environment(vault_host, artsy_env):
    raise Exception(
      f'Hostname {vault_host} does not agree with environment {artsy_env}'
    )


if __name__ == "__main__":

  args = parse_args()
  artsy_env, artsy_project, repos_base_dir, dry_run, loglevel = (
    args.artsy_env,
    args.artsy_project,
    args.repos_base_dir,
    args.dry_run,
    args.loglevel,
  )

  setup_logging(eval('logging.' + loglevel))

  vault_host, vault_port, kvv2_mount_point = parse_env()

  validate(artsy_env, vault_host, vault_port)

  migrate_config_secrets(
    artsy_env,
    artsy_project,
    repos_base_dir,
    vault_host,
    vault_port,
    kvv2_mount_point,
    dry_run
  )
