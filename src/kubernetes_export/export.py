import argparse
import logging
import os

import kubernetes_export.context

from kubernetes_export.export import export_and_backup
from lib.logging import setup_logging


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

def parse_env():
  ''' parse env vars '''
  s3_bucket = os.environ.get('K8S_BACKUP_S3_BUCKET', '')
  s3_prefix = os.environ.get('K8S_BACKUP_S3_PREFIX', 'dev')
  # local dir to store yamls exported from Kubernetes
  local_dir = os.environ.get('LOCAL_DIR', '/tmp/kubernetes_resources')
  return local_dir, s3_bucket, s3_prefix

def validate(s3, s3_bucket):
  ''' validate config obtained from env and command line '''
  if s3 and not s3_bucket:
    raise Exception("K8S_BACKUP_S3_BUCKET must be specified in the environment.")


if __name__ == "__main__":

  args = parse_args()
  artsy_env, in_cluster, loglevel, s3 = (
    args.artsy_env,
    args.in_cluster,
    args.loglevel,
    args.s3
  )

  setup_logging(eval('logging.' + loglevel))

  local_dir, s3_bucket, s3_prefix = parse_env()

  validate(s3, s3_bucket)

  KUBERNETES_OBJECTS = [
    'configmaps',
    'cronjobs',
    'daemonsets',
    'deployments',
    'externalsecrets',
    'horizontalpodautoscalers',
    'ingresses',
    'persistentvolumeclaims',
    'poddisruptionbudgets',
    'replicationcontrollers',
    'rolebindings',
    'roles',
    'secrets',
    'serviceaccounts',
    'services',
    'statefulsets'
  ]
  export_and_backup(KUBERNETES_OBJECTS, artsy_env, in_cluster, local_dir, s3, s3_bucket, s3_prefix)
