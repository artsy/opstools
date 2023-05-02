import os

import argparse
import logging

import kubernetes_cleanup_namespaces.context
from lib.logging import setup_logging

class AppConfig:
  ''' get env config and validate them '''
  def __init__(self, env):

    print('AppConfig __init__')
    # set this if running locally
    self.context = env.get('KUBECTL_CONTEXT', '')

    # set this if running inside kubernetes
    self.k8s_cluster = env.get('K8S_CLUSTER', '')

    validate(self.context, self.k8s_cluster)

    args = parse_args()
    self.force, self.loglevel, self.ndays = args.force, args.loglevel, int(args.ndays)
    setup_logging(eval('logging.' + self.loglevel))

def parse_args():
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


def validate(context, k8s_cluster):
  ''' validate params obtained from env '''
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
