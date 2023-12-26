import argparse
import logging
import os

import kubernetes_cleanup_pods.context

from lib.logging import setup_logging

from kubernetes_cleanup_pods.pods import (
  cleanup_pods
)


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
    'nhours',
    help='limit deletion to pods older than n hours'
  )
  parser.add_argument(
    '--completed',
    action='store_true',
    help='limit deletion to completed pods'
  )
  parser.add_argument(
    '--force',
    action='store_true',
    help='to really delete'
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
    '--name',
    help='limit deletion to this pod name'
  )
  parser.add_argument(
    '--namespace',
    default='default',
    help='namespace to delete pods from'
  )
  return parser.parse_args()


if __name__ == "__main__":

  args = parse_args()
  (
    loglevel,
    artsy_env,
    completed,
    force,
    in_cluster,
    name,
    namespace,
    nhours
  ) = (
    args.loglevel,
    args.artsy_env,
    args.completed,
    args.force,
    args.in_cluster,
    args.name,
    args.namespace,
    int(args.nhours)
  )

  setup_logging(eval('logging.' + loglevel))

  cleanup_pods(
    artsy_env,
    completed,
    force,
    in_cluster,
    name,
    namespace,
    nhours
  )
