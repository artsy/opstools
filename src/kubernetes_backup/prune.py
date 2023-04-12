#!/usr/bin/env python

import os
import sys

import argparse
import logging

from kubernetes_backup.backup import prune
from kubernetes_backup.config import setup_logging

def parse_args():
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument('--force', action='store_true', help='to actually delete')
  parser.add_argument('--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  return parser.parse_args()

def get_env():
  ''' get vars from env '''

  # set this if running locally
  context = os.environ.get('KUBECTL_CONTEXT', '')

  # set this if running inside kubernetes
  k8s_cluster = os.environ.get('K8S_CLUSTER', '')

  # S3 bucket that holds backups
  s3_bucket = os.environ.get('K8S_BACKUP_S3_BUCKET', '')

  # S3 prefix that holds backups
  s3_prefix = os.environ.get('K8S_BACKUP_S3_PREFIX', 'dev/backups')

  # number of most recent backups to keep
  keepn_str = os.environ.get('K8S_BACKUP_KEEPN')

  return context, k8s_cluster, s3_bucket, s3_prefix, keepn_str

def validate(context, k8s_cluster, s3_bucket, keepn):
  ''' validate params obtained from env and command line '''
  if not context and not k8s_cluster:
    sys.exit("Error: either KUBECTL_CONTEXT or K8S_CLUSTER must be specified in the environment")

  if context and k8s_cluster:
    sys.exit("Error: KUBECTL_CONTEXT and K8S_CLUSTER must not both be specified in the environment")

  if not s3_bucket:
    sys.exit("Error: K8S_BACKUP_S3_BUCKET must be specified in the environment")

  if not keepn_str:
    sys.exit("Error: K8S_BACKUP_KEEPN must be specified in the environment")

######
# main
######

args = parse_args()
force, loglevel = (args.force, args.loglevel)

setup_logging(eval('logging.' + loglevel))

context, k8s_cluster, s3_bucket, s3_prefix, keepn_str = get_env()

validate(context, k8s_cluster, s3_bucket, keepn_str)

prune(context, k8s_cluster, s3_bucket, s3_prefix, int(keepn_str), force)
