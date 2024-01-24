import argparse
import logging
import os

import vault_snapshot.context

from lib.logging import setup_logging
from lib.util import is_artsy_s3_bucket

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
  vault_addr = os.environ.get('VAULT_ADDR')
  vault_user = os.environ.get('VAULT_USER')
  vault_pass = os.environ.get('VAULT_PASS')
  s3_bucket = os.environ.get('VAULT_BACKUP_S3_BUCKET', '')
  s3_prefix = os.environ.get('VAULT_BACKUP_S3_PREFIX', 'dev')
  # local dir to store snapshot
  local_dir = os.environ.get(
    'LOCAL_DIR', '/tmp/vault_snapshot'
  )
  return (
    local_dir,
    vault_addr,
    vault_user,
    vault_pass,
    s3_bucket,
    s3_prefix
  )

def validate(vault_addr, vault_user, vault_pass, s3, s3_bucket):
  ''' validate config obtained from env and command line '''
  if not (vault_addr and vault_user and vault_pass):
    raise Exception(
      "The following environment variables must be specified: " +
      "VAULT_ADDR, VAULT_USER, VAULT_PASS"
    )
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
    vault_addr,
    vault_user,
    vault_pass,
    s3_bucket,
    s3_prefix
  ) = parse_env()

  validate(
    vault_addr,
    vault_user,
    vault_pass,
    s3,
    s3_bucket
  )

  take_snapshot(
    local_dir,
    artsy_env,
    vault_addr,
    vault_user,
    vault_pass,
    s3,
    s3_bucket,
    s3_prefix
  )
