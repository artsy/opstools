#!/usr/bin/env python

import os
import sys

import argparse
import logging

from kubernetes_backup.backup import export_and_backup
from kubernetes_backup.config import setup_logging

def parse_args():
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument('--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  parser.add_argument('--s3', action='store_true', help='whether to backup to s3')
  return parser.parse_args()

def get_env():
  ''' get vars from env '''

  # set this if running locally
  context = os.environ.get('KUBECTL_CONTEXT', '')

  # set this if running inside kubernetes
  k8s_cluster = os.environ.get('K8S_CLUSTER', '')

  # S3 bucket to backup to
  s3_bucket = os.environ.get('K8S_BACKUP_S3_BUCKET', '')

  # S3 prefix to backup under
  s3_prefix = os.environ.get('K8S_BACKUP_S3_PREFIX', 'dev/backups')

  # local dir to store yamls exported from Kubernetes
  basedir = os.environ.get('BASEDIR', '/tmp/kubernetes-backups')

  return context, k8s_cluster, basedir, s3_bucket, s3_prefix

def validate(context, k8s_cluster, s3, s3_bucket):
  ''' validate params obtained from env and command line '''

  if not context and not k8s_cluster:
    sys.exit("Error: either KUBECTL_CONTEXT or K8S_CLUSTER must be specified in the environment")

  if context and k8s_cluster:
    sys.exit("Error: KUBECTL_CONTEXT and K8S_CLUSTER must not both be specified in the environment")

  if s3 and not s3_bucket:
    sys.exit("Error: K8S_BACKUP_S3_BUCKET must be specified in the environment")

  # sanity check S3 bucket name
  if not s3_bucket.startswith('artsy-'):
    sys.exit(f"Error: It seems {s3_bucket} is not an Artsy S3 bucket.")

######
# main
######

args = parse_args()
loglevel, s3 = args.loglevel, args.s3

setup_logging(eval('logging.' + loglevel))

context, k8s_cluster, basedir, s3_bucket, s3_prefix = get_env()

validate(context, k8s_cluster, s3, s3_bucket)

KUBERNETES_OBJECTS = [
  'configmaps',
  'cronjobs',
  'daemonsets',
  'deployments',
  'horizontalpodautoscalers',
  'ingresses',
  'persistentvolumeclaims',
  'poddisruptionbudgets',
  'replicationcontrollers',
  'rolebindings',
  'roles',
  'secrets',
  'services',
  'statefulsets'
]

export_and_backup(context, k8s_cluster, basedir, s3, s3_bucket, s3_prefix, KUBERNETES_OBJECTS)