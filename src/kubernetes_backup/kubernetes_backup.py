#!/usr/bin/env python

from kubernetes_backup.backup import export_and_backup
from kubernetes_backup.config import get_env

context, k8s_cluster, basedir, to_s3, s3_bucket, s3_prefix = get_env()

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

export_and_backup(context, k8s_cluster, basedir, to_s3, s3_bucket, s3_prefix, KUBERNETES_OBJECTS)
