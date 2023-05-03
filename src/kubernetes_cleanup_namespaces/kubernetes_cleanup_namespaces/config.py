import os

import argparse
import logging

import kubernetes_cleanup_namespaces.context
from lib.logging import setup_logging

class AppConfig:
  def __init__(self, args, env):
    ''' set app-wide configs and initialize the app '''
    force, loglevel, ndays = args.force, args.loglevel, int(args.ndays)
    context = env

    self.context = context
    self.force = force
    self.ndays = ndays

    self.protected_namespaces = [
      'cert-manager',
      'data-application',
      'default',
      'ingress-nginx',
      'kube-node-lease',
      'kube-public',
      'kubernetes-dashboard',
      'kube-system'
    ]

    self._init_app(loglevel)

  def _init_app(self, loglevel):
    ''' initialize the app '''
    # initialize logging
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
  ''' parse and validate env vars '''
  # set this var if running locally
  # omit it if running inside a kubernetes cluster
  context = env.get('KUBECTL_CONTEXT', '')

  return context

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args(), parse_env(os.environ))
