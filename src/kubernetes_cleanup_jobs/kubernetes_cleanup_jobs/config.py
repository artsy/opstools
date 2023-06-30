import os
import argparse
import logging

import kubernetes_cleanup_jobs.context
from lib.logging import setup_logging

class AppConfig:
  def __init__(self, cmdline_args):
    ''' set app-wide configs and initialize the app '''
    (
      loglevel,
      self.all,
      self.artsy_env,
      self.completed,
      self.force,
      self.in_cluster,
      self.name,
      self.namespace,
      self.nhours
    ) = (
      cmdline_args.loglevel,
      cmdline_args.all,
      cmdline_args.artsy_env,
      cmdline_args.completed,
      cmdline_args.force,
      cmdline_args.in_cluster,
      cmdline_args.name,
      cmdline_args.namespace,
      int(cmdline_args.nhours)
    )
    self._init_app(loglevel)

  def _init_app(self, loglevel):
    ''' initialize the app '''
    setup_logging(eval('logging.' + loglevel))

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
  group.add_argument(
    '--completed',
    action='store_true',
    help='delete completed jobs'
  )
  parser.add_argument(
    '--force',
    action='store_true',
    help='to really delete'
  )
  parser.add_argument(
    '--in_cluster',
    action='store_true',
    help='indicates the script is being run inside the k8s cluster to be cleaned up'
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
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument(
    '--all',
    action='store_true',
    help='delete all jobs'
  )
  group.add_argument(
    '--name',
    help='delete jobs by name'
  )
  return parser.parse_args()

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args())
