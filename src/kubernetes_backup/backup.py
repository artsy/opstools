import os
import sys

import argparse
import logging

import kubernetes_backup.context
from lib.logging import setup_logging

from kubernetes_backup.backup import export_and_backup

if __name__ == "__main__":

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
    'serviceaccounts',
    'services',
    'statefulsets'
  ]
  export_and_backup(KUBERNETES_OBJECTS)
