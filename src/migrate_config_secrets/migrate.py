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
    '--dry-run',
    action="store_true",
    help=("Dry Run. Won't make any changes.")
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
  parser.add_argument(
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  return parser.parse_args()

def parse_env():
  ''' parse env vars '''
  vault_addr = os.environ.get('VAULT_ADDR')
  vault_token = os.environ.get('VAULT_TOKEN')
  kvv2_mount_point = os.environ.get('VAULT_KVV2_MOUNT_POINT')
  return vault_addr, kvv2_mount_point, vault_token

def validate(artsy_env, vault_addr):
  ''' validate config obtained from env and command line '''
  if not vault_addr:
    raise Exception(
      "The following environment variables must be specified: " +
      "VAULT_ADDR"
    )
  # make sure Vault address matches environment
  # in case user specifies 'staging' on the command line
  # yet supplies production Vault address in Env (and connects to Prod VPN)
  # or the other way around
  # address for staging is expected to contain 'stg'
  # that for prod contain 'prd'
  if artsy_env == 'staging' and not 'stg' in vault_addr:
    raise Exception(f'Vault address does not contain "stg": {vault_addr}')
  elif artsy_env == 'production' and not 'prd' in vault_addr:
    raise Exception(f'Vault address does not contain "prd": {vault_addr}')


if __name__ == "__main__":

  args = parse_args()
  artsy_env, artsy_project, repos_base_dir, dry_run, list, loglevel = (
    args.artsy_env,
    args.artsy_project,
    args.repos_base_dir,
    args.dry_run,
    args.list,
    args.loglevel,
  )

  setup_logging(eval('logging.' + loglevel))

  vault_addr, kvv2_mount_point, vault_token = parse_env()

  validate(artsy_env, vault_addr)

  migrate_config_secrets(
    artsy_env,
    artsy_project,
    list,
    repos_base_dir,
    vault_addr,
    kvv2_mount_point,
    vault_token,
    dry_run
  )
