import argparse
import logging
import os

import kubernetes_configmap_jwt_scan.context

from lib.logging import setup_logging

from kubernetes_configmap_jwt_scan.scan import scan


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
  return parser.parse_args()


if __name__ == "__main__":

  args = parse_args()
  loglevel, artsy_env, in_cluster = (
    args.loglevel,
    args.artsy_env,
    args.in_cluster
  )

  setup_logging(eval('logging.' + loglevel))

  scan(loglevel, artsy_env, in_cluster)
