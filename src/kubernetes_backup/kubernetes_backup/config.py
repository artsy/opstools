import os
import sys

def get_env():
  ''' get vars from env '''

  # set this if running locally
  context = os.environ.get('KUBECTL_CONTEXT', '')

  # set this if running inside kubernetes
  k8s_cluster = os.environ.get('K8S_CLUSTER', '')

  # set to 'true' to back up to S3
  to_s3 = os.getenv("K8S_BACKUP_TO_S3", 'False').lower() in ('true', '1', 't')

  # S3 bucket to backup to
  s3_bucket = os.environ.get('K8S_BACKUP_S3_BUCKET', '')

  # S3 prefix to backup under
  s3_prefix = os.environ.get('K8S_BACKUP_S3_PREFIX', 'dev/backups')

  # local dir to store yamls exported from Kubernetes
  basedir = os.environ.get('BASEDIR', '/tmp/kubernetes-backups')

  if not context and not k8s_cluster:
    sys.exit('Error: either KUBECTL_CONTEXT or K8S_CLUSTER must be specified in the environment')

  if context and k8s_cluster:
    sys.exit('Error: KUBECTL_CONTEXT and K8S_CLUSTER must not both be specified in the environment')

  if to_s3 and not s3_bucket:
    sys.exit('Error: K8S_BACKUP_S3_BUCKET must be specified in the environment')

  # sanity check S3 bucket name
  if not s3_bucket.startswith('artsy-'):
    sys.exit("Error: It seems '%s' is not an Artsy S3 bucket." %s3_bucket)

  return context, k8s_cluster, basedir, to_s3, s3_bucket, s3_prefix
