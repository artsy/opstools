import os
import sys

import argparse
import logging

import kubernetes_backup.context
from lib.logging import setup_logging

class AppConfig:
  def __init__(self, cmdline_args, env):
    ''' set app-wide configs and initialize the app '''
    loglevel, self.s3 = (
      cmdline_args.loglevel,
      cmdline_args.s3
    )
    self.context, self.k8s_cluster, self.local_dir, self.s3_bucket, self.s3_prefix = env
    validate(self.context, self.k8s_cluster, self.s3, self.s3_bucket)
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
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  parser.add_argument(
    '--s3',
    action='store_true',
    help='whether to backup to s3'
  )
  return parser.parse_args()

def parse_env(env):
  ''' parse and validate env vars '''

  # set this if running locally
  context = os.environ.get('KUBECTL_CONTEXT', '')

  # set this if running inside kubernetes
  k8s_cluster = os.environ.get('K8S_CLUSTER', '')

  # S3 bucket to backup to
  s3_bucket = os.environ.get('K8S_BACKUP_S3_BUCKET', '')

  # S3 prefix to backup under
  s3_prefix = os.environ.get('K8S_BACKUP_S3_PREFIX', 'dev')

  # local dir to store yamls exported from Kubernetes
  local_dir = os.environ.get('LOCAL_DIR', '/tmp/kubernetes_resources')

  return context, k8s_cluster, local_dir, s3_bucket, s3_prefix

def validate(context, k8s_cluster, s3, s3_bucket):
  ''' validate params obtained from env and command line '''
  if not context and not k8s_cluster:
    sys.exit(
      "Error: either KUBECTL_CONTEXT or K8S_CLUSTER must be specified in the environment"
    )

  if context and k8s_cluster:
    sys.exit(
      "Error: KUBECTL_CONTEXT and K8S_CLUSTER must not both be specified in the environment"
    )

  if s3 and not s3_bucket:
    sys.exit(
      "Error: K8S_BACKUP_S3_BUCKET must be specified in the environment"
    )

  # sanity check S3 bucket name
  if s3_bucket and not s3_bucket.startswith('artsy-'):
    sys.exit(
      f"Error: It seems {s3_bucket} is not an Artsy S3 bucket."
    )

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args(), parse_env(os.environ))
