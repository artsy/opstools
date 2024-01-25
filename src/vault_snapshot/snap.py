import argparse
import logging
import os

import vault_snapshot.context

from lib.logging import setup_logging
from lib.validations import is_artsy_s3_bucket

from vault_snapshot.snap import (
  take_snapshot
)


def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument(
    'artsy_env',
    choices=['staging', 'production'],
    help='the artsy environment of the Vault instance'
  )
  parser.add_argument(
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  parser.add_argument(
    '--s3',
    action='store_true',
    help='indicates to save snapshot to s3'
  )
  return parser.parse_args()

def parse_env():
  ''' parse env vars '''
  vault_host = os.environ.get('VAULT_HOST')
  vault_port = os.environ.get('VAULT_PORT')
  s3_bucket = os.environ.get('VAULT_BACKUP_S3_BUCKET', '')
  s3_prefix = os.environ.get('VAULT_BACKUP_S3_PREFIX', 'dev')
  # local dir to store snapshot
  local_dir = os.environ.get(
    'LOCAL_DIR', '/tmp/vault_snapshot'
  )
  return (
    local_dir,
    vault_host,
    vault_port,
    s3_bucket,
    s3_prefix
  )

def validate(artsy_env, vault_host, vault_port, s3, s3_bucket):
  ''' validate config obtained from env and command line '''

  if not (vault_host and vault_port):
    raise Exception(
      "The following environment variables must be specified: " +
      "VAULT_HOST, " +
      "VAULT_PORT"
    )

  # make sure Vault hostname matches environment
  # in case user specifies 'staging' on the command line
  # yet supplies production Vault host in Env (and connects to Prod VPN)
  # or the other way around
  # address for staging is expected to contain 'stg'
  # that for prod contain 'prd'
  if artsy_env == 'staging' and not 'stg' in vault_host:
    raise Exception(f'Vault hostname does not contain "stg": {vault_host}')
  elif artsy_env == 'production' and not 'prd' in vault_host:
    raise Exception(f'Vault hostname does not contain "prd": {vault_host}')

  if s3 and not s3_bucket:
    raise Exception(
      "VAULT_BACKUP_S3_BUCKET must be specified in the environment."
    )
  if s3 and not is_artsy_s3_bucket(s3_bucket):
    raise Exception(f"{s3_bucket} seems not an Artsy S3 bucket.")


if __name__ == "__main__":

  args = parse_args()
  loglevel, artsy_env, s3 = (
    args.loglevel,
    args.artsy_env,
    args.s3
  )

  setup_logging(eval('logging.' + loglevel))

  (
    local_dir,
    vault_host,
    vault_port,
    s3_bucket,
    s3_prefix
  ) = parse_env()

  validate(
    artsy_env,
    vault_host,
    vault_port,
    s3,
    s3_bucket
  )

  take_snapshot(
    local_dir,
    artsy_env,
    vault_host,
    vault_port,
    s3,
    s3_bucket,
    s3_prefix
  )
