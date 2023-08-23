import argparse
import logging
import os

import kubernetes_cleanup_namespaces.context

from lib.logging import setup_logging

class AppConfig:
  def __init__(self, cmdline_args):
    ''' set app-wide configs and initialize the app '''
    (
      loglevel,
      self.artsy_env,
      self.force,
      self.in_cluster,
      self.ndays
    )= (
      cmdline_args.loglevel,
      cmdline_args.artsy_env,
      cmdline_args.force,
      cmdline_args.in_cluster,
      int(cmdline_args.ndays)
    )
    self.protected_namespaces = [
      'cert-manager',
      'circleci',
      'default',
      'external-secrets',
      'ingress-nginx',
      'kube-node-lease',
      'kube-public',
      'kubernetes-dashboard',
      'kube-system',
      'vault'
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
    'artsy_env',
    choices=['staging', 'production'],
    help='the artsy environment of the Kubernetes cluster'
  )
  parser.add_argument(
    'ndays',
    help='delete namespaces older than n days'
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

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args())
