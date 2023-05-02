import os

import argparse
import logging

import kubernetes_cleanup_namespaces.context
from lib.logging import setup_logging

class AppConfig:
  def __init__(self, env, args):
    ''' set app-wide configs and initialize the app '''
    force, loglevel, ndays = args.force, args.loglevel, int(args.ndays)
    context, k8s_cluster = env

    self.context = context
    self.k8s_cluster = k8s_cluster
    self.force = force
    self.ndays = ndays

    self._init_app(loglevel)

  @classmethod
  def _init_app(cls, loglevel):
    ''' initialize the app '''
    setup_logging(eval('logging.' + loglevel))

def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument(
    'ndays',
    help='delete namespaces older than n days'
  )
  parser.add_argument(
    '--force',
    action='store_true',
    help='to actually delete'
  )
  parser.add_argument(
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  return parser.parse_args()

def parse_env(env):
  ''' parse env vars '''
  # set this if running locally
  context = env.get('KUBECTL_CONTEXT', '')
  # set this if running inside kubernetes
  k8s_cluster = env.get('K8S_CLUSTER', '')
  validate(context, k8s_cluster)
  return context, k8s_cluster

def validate(context, k8s_cluster):
  ''' validate params '''
  if not context and not k8s_cluster:
    sys.exit(
      "Error: either KUBECTL_CONTEXT or K8S_CLUSTER must be specified in the environment"
    )
  if context and k8s_cluster:
    sys.exit(
      "Error: KUBECTL_CONTEXT and K8S_CLUSTER must not both be specified in the environment"
  )

# import this from other modules in order to instantiate
config = AppConfig(parse_env(os.environ), parse_args())
