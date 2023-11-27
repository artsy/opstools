import argparse
import logging
import os

import kubernetes_cleanup_review_apps.context

from kubernetes_cleanup_review_apps.cleanup import (
  cleanup_review_apps
)
from lib.logging import setup_logging


def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description=('Delete old review apps')
  )
  parser.add_argument(
    'ndays',
    help='delete review apps older than n days'
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
  return parser.parse_args()


if __name__ == "__main__":

  args = parse_args()
  ndays, force, in_cluster, loglevel = (
    args.ndays,
    args.force,
    args.in_cluster,
    args.loglevel,
  )

  setup_logging(eval('logging.' + loglevel))

  cleanup_review_apps(int(ndays), force, in_cluster)
