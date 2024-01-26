import argparse
import logging
import os

import rabbitmq_export.context

from lib.logging import setup_logging

from rabbitmq_export.export import (
  export_and_backup
)


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
    help='indicates to save broker definition to s3'
  )
  return parser.parse_args()

def parse_env():
  ''' parse env vars '''
  rabbitmq_host = os.environ.get('RABBITMQ_HOST')
  rabbitmq_user = os.environ.get('RABBITMQ_USER')
  rabbitmq_pass = os.environ.get('RABBITMQ_PASS')
  s3_bucket = os.environ.get('RABBITMQ_BACKUP_S3_BUCKET', '')
  s3_prefix = os.environ.get('RABBITMQ_BACKUP_S3_PREFIX', 'dev')
  # local dir to store exported broker definitions
  local_dir = os.environ.get(
    'LOCAL_DIR', '/tmp/rabbitmq_broker_definitions'
  )
  return (
    local_dir,
    rabbitmq_host,
    rabbitmq_user,
    rabbitmq_pass,
    s3_bucket,
    s3_prefix
  )

def validate(rabbitmq_host, rabbitmq_user, rabbitmq_pass, s3, s3_bucket):
  ''' validate config obtained from env and command line '''
  if not (rabbitmq_host and rabbitmq_user and rabbitmq_pass):
    raise Exception(
      "The following environment variables must be specified: " +
      "RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASS"
    )
  if not hostname_agrees_with_artsy_environment(rabbitmq_host, artsy_env):
    raise Exception(
      f'Hostname {rabbitmq_host} does not agree with environment {artsy_env}'
    )
  if s3 and not s3_bucket:
    raise Exception(
      "RABBITMQ_BACKUP_S3_BUCKET must be specified in the environment."
    )


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
    rabbitmq_host,
    rabbitmq_user,
    rabbitmq_pass,
    s3_bucket,
    s3_prefix
  ) = parse_env()

  validate(
    rabbitmq_host,
    rabbitmq_user,
    rabbitmq_pass,
    s3,
    s3_bucket
  )

  export_and_backup(
    local_dir,
    artsy_env,
    rabbitmq_host,
    rabbitmq_user,
    rabbitmq_pass,
    s3,
    s3_bucket,
    s3_prefix
  )
