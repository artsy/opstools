import os

import argparse
import logging

import kubernetes_cleanup_namespaces.context
from lib.logging import setup_logging

class AppConfig:
  def __init__(self, env):
    ''' initializes the app '''
    args = self._parse_args()
    force, loglevel, ndays = args.force, args.loglevel, int(args.ndays)

    context, k8s_cluster = self._parse_env(env)
    self._validate(context, k8s_cluster)

    self.context = context
    self.k8s_cluster = k8s_cluster
    self.force = force
    self.ndays = ndays

    setup_logging(eval('logging.' + loglevel))

  @classmethod
  def _parse_args(cls):
    ''' parse command line arguments '''
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

  @classmethod
  def _parse_env(cls, env):
    ''' parse env vars '''
    # set this if running locally
    context = env.get('KUBECTL_CONTEXT', '')
    # set this if running inside kubernetes
    k8s_cluster = env.get('K8S_CLUSTER', '')
    return context, k8s_cluster

  @classmethod
  def _validate(cls, context, k8s_cluster):
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
config = AppConfig(os.environ)
