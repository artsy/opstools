import argparse
import logging
import os
import sys

import rabbitmq_export_definitions.context
from lib.logging import setup_logging

class AppConfig:
  def __init__(self, cmdline_args, env):
    ''' set app-wide configs and initialize the app '''
    loglevel, self.artsy_env, self.s3 = (
      cmdline_args.loglevel,
      cmdline_args.artsy_env,
      cmdline_args.s3
    )
    self.local_dir, self.rabbitmq_host, self.rabbitmq_user, self.rabbitmq_pass, self.s3_bucket, self.s3_prefix = env

    if self.s3 and not self.s3_bucket:
      sys.exit(
        "Error: The following environment variables must be specified: RABBITMQ_BACKUP_S3_BUCKET"
      )
  
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
    'artsy_env',
    choices=['staging', 'production'],
    help='the artsy environment of the RabbitMQ instance'
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
    help='whether to save broker definition to s3'
  )
  return parser.parse_args()

def parse_env(env):
  ''' parse and validate env vars '''
  # set this var if running locally
  # omit it if running inside a kubernetes cluster
  rabbitmq_host = env.get('RABBITMQ_HOST')
  rabbitmq_user = env.get('RABBITMQ_USER')
  rabbitmq_pass = env.get('RABBITMQ_PASS')

  s3_bucket = env.get('RABBITMQ_BACKUP_S3_BUCKET', '')
  s3_prefix = env.get('RABBITMQ_BACKUP_S3_PREFIX', 'dev')

  # local dir to store exported broker definitions
  local_dir = os.environ.get('LOCAL_DIR', '/tmp/rabbitmq_broker_definitions')

  if not (rabbitmq_host and rabbitmq_user and rabbitmq_pass):
    sys.exit(
      "Error: The following environment variables must be specified: RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASS"
    )
  return local_dir, rabbitmq_host, rabbitmq_user, rabbitmq_pass, s3_bucket, s3_prefix

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args(), parse_env(os.environ))
