import argparse
import os

import load_secrets_from_vault.context

from load_secrets_from_vault.load import load_secrets
from lib.logging import setup_logging
from lib.validations import (
  hostname_agrees_with_artsy_environment
)


def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument(
    'artsy_env',
    choices=['staging', 'production'],
    help='the artsy environment of the Kubernetes cluster'
  )
  parser.add_argument(
    'artsy_project',
    help='artsy project'
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
  secrets_file = os.environ.get('SECRETS_FILE', '')

  return vault_host, vault_port, kvv2_mount_point, secrets_file

def validate(artsy_env, vault_host, vault_port, secrets_file):
  ''' validate config obtained from env and command line '''
  if not (vault_host and vault_port and secrets_file):
    raise Exception(
      "The following environment variables must be specified: " +
      "VAULT_HOST, " +
      "VAULT_PORT, " +
      "SECRETS_FILE"
    )
  if not hostname_agrees_with_artsy_environment(vault_host, artsy_env):
    raise Exception(
      f'Hostname {vault_host} does not agree with environment {artsy_env}'
    )


if __name__ == "__main__":

  args = parse_args()
  artsy_env, artsy_project, loglevel = (
    args.artsy_env,
    args.artsy_project,
    args.loglevel,
  )

  setup_logging(eval('logging.' + loglevel))

  vault_host, vault_port, kvv2_mount_point, secrets_file = parse_env()

  validate(artsy_env, vault_host, vault_port, secrets_file)

  load_secrets(artsy_project, vault_host, vault_port, secrets_file, kvv2_mount_point)
