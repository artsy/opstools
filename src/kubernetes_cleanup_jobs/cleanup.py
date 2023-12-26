import argparse
import logging
import os

import kubernetes_cleanup_jobs.context

from lib.logging import setup_logging

from kubernetes_cleanup_jobs.jobs import (
  cleanup_jobs
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
    help='delete jobs older than n hours'
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
    '--namespace',
    default='default',
    help='namespace to delete jobs in'
  )
  return parser.parse_args()


if __name__ == "__main__":

  args = parse_args()

  (
    loglevel,
    artsy_env,
    force,
    in_cluster,
    namespace,
    nhours
  ) = (
    args.loglevel,
    args.artsy_env,
    args.force,
    args.in_cluster,
    args.namespace,
    int(args.nhours)
  )

  setup_logging(eval('logging.' + loglevel))

  cleanup_jobs(
    loglevel,
    artsy_env,
    force,
    in_cluster,
    namespace,
    nhours
  )
