import argparse
import logging
import os

import s3_prune_backups.context

from s3_prune_backups.prune_backups import prune
from lib.logging import setup_logging


def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument(
    'app',
    help="which app's backups to prune, example: k8s, rabbitmq, ..."
  )
  parser.add_argument(
    'artsy_env',
    choices=['staging', 'production'],
    help='the artsy environment to prune backups in'
  )
  parser.add_argument(
    'ndays',
    help='backups older than ndays will be pruned'
  )
  parser.add_argument(
    'suffix',
    help='suffix of the backup files, example: json, tar.gz, ...'
  )
  parser.add_argument(
    '--force',
    action='store_true',
    help='really delete the backups'
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
  s3_bucket = os.environ.get('BACKUP_S3_BUCKET', '')
  s3_prefix = os.environ.get('BACKUP_S3_PREFIX', 'dev')
  return s3_bucket, s3_prefix

def validate(s3_bucket):
  ''' validate config obtained from env and command line '''
  if not s3_bucket:
    raise Exception(
      'BACKUP_S3_BUCKET must be specified in the environment.'
    )


if __name__ == "__main__":

  args = parse_args()
  loglevel, app, artsy_env, force, ndays, suffix = (
    args.loglevel,
    args.app,
    args.artsy_env,
    args.force,
    int(args.ndays),
    args.suffix
  )

  setup_logging(eval('logging.' + loglevel))

  s3_bucket, s3_prefix = parse_env()
  validate(s3_bucket)

  prune(
    app,
    artsy_env,
    ndays,
    s3_bucket,
    s3_prefix,
    suffix,
    force
  )
