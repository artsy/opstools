import argparse
import logging
import os
import sys

import s3_prune_backups.context

from lib.logging import setup_logging

class AppConfig:
  def __init__(self, cmdline_args, env):
    ''' set app-wide configs and initialize the app '''
    loglevel, self.app, self.artsy_env, self.ndays, self.suffix, self.force = (
      cmdline_args.loglevel,
      cmdline_args.app,
      cmdline_args.artsy_env,
      int(cmdline_args.ndays),
      cmdline_args.suffix,
      cmdline_args.force
    )
    self.s3_bucket, self.s3_prefix = env
    self._init_app(loglevel)

  def _init_app(self, loglevel):
    ''' initialize the app '''
    # initialize logging
    setup_logging(eval('logging.' + loglevel))

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
    help='the artsy environment of the RabbitMQ instance'
  )
  parser.add_argument(
    'ndays',
    help='number of days worth of backups to keep'
  )
  parser.add_argument(
    'suffix',
    help='suffix of the backup files, example: json, tar.gz, ...'
  )
  parser.add_argument(
    '--force',
    action='store_true',
    help='to actually delete'
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
  s3_bucket = env.get('RABBITMQ_BACKUP_S3_BUCKET', '')
  s3_prefix = env.get('RABBITMQ_BACKUP_S3_PREFIX', 'dev')
  return s3_bucket, s3_prefix

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args(), parse_env(os.environ))
