import argparse
import logging

import kubernetes_cleanup_pods.context

from lib.logging import setup_logging

class AppConfig:
  def __init__(self, cmdline_args, env):
    ''' set app-wide configs and initialize the app '''
    self.nhours, self.name, self.completed, self.namespace, self.force, self.loglevel, self.artsy_env, self.in_cluster = (
      int(cmdline_args.nhours),
      cmdline_args.name,
      cmdline_args.completed,
      cmdline_args.namespace,
      cmdline_args.force,
      cmdline_args.loglevel,
      cmdline_args.artsy_env,
      cmdline_args.in_cluster
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
    '--in_cluster',
    action='store_true',
    help='whether the script is run from within the k8s cluster itself'
  )
  parser.add_argument(
    'nhours',
    help='delete pods older than n hours'
  )
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument(
    '--name',
    help='delete pods by name'
  )
  group.add_argument(
    '--completed',
    action='store_true',
    help='delete completed pods'
  )
  parser.add_argument(
    '--namespace',
    default='default',
    help='namespace to delete pods from'
  )
  parser.add_argument(
    '--force',
    action='store_true',
    help='to actually cleanup'
  )
  parser.add_argument(
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  return parser.parse_args()

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args())
