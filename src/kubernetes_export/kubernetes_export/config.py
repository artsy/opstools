import argparse
import logging
import os
import sys

import kubernetes_export.context

from lib.logging import setup_logging
from lib.util import error_exit, is_artsy_s3_bucket

class AppConfig:
  def __init__(self, cmdline_args, env):
    ''' set app-wide configs and initialize the app '''
    loglevel, self.artsy_env, self.in_cluster, self.s3 = (
      cmdline_args.loglevel,
      cmdline_args.artsy_env,
      cmdline_args.in_cluster,
      cmdline_args.s3
    )
    self.local_dir, self.s3_bucket, self.s3_prefix = env
    validate(self.s3, self.s3_bucket)
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
    help='the artsy environment of the Kubernetes cluster'
  )
  parser.add_argument(
    '--in_cluster',
    action='store_true',
    help='indicates the script is being run inside the target k8s cluster'
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
    help='indicates to save backup to S3'
  )
  return parser.parse_args()

def parse_env(env):
  ''' parse env vars '''
  s3_bucket = os.environ.get('K8S_BACKUP_S3_BUCKET', '')
  s3_prefix = os.environ.get('K8S_BACKUP_S3_PREFIX', 'dev')
  # local dir to store yamls exported from Kubernetes
  local_dir = os.environ.get('LOCAL_DIR', '/tmp/kubernetes_resources')
  return local_dir, s3_bucket, s3_prefix

def validate(s3, s3_bucket):
  ''' validate config obtained from env and command line '''
  if s3 and not s3_bucket:
    error_exit("K8S_BACKUP_S3_BUCKET must be specified in the environment.")
  if s3 and not is_artsy_s3_bucket(s3_bucket):
    error_exit(f"{s3_bucket} seems not an Artsy S3 bucket.")

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args(), parse_env(os.environ))
