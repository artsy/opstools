import os
import argparse
import logging

import kubernetes_cleanup_jobs.context
from lib.logging import setup_logging

class AppConfig:
  def __init__(self, cmdline_args, env):
    ''' set app-wide configs and initialize the app '''
    nhours, name, completed, all, namespace, force, loglevel = (
      int(cmdline_args.nhours),
      cmdline_args.name,
      cmdline_args.completed,
      cmdline_args.all,
      cmdline_args.namespace,
      cmdline_args.force,
      cmdline_args.loglevel,
    )

    context = env

    self.nhours = nhours
    self.name = name
    self.completed = completed
    self.all = all
    self.namespace = namespace
    self.force = force
    self.context = context

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
    'nhours',
    help='delete jobs older than n hours'
  )
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument(
    '--name',
    help='delete jobs by name'
  )
  group.add_argument(
    '--completed',
    action='store_true',
    help='delete completed jobs'
  )
  group.add_argument(
    '--all',
    action='store_true',
    help='delete all jobs'
  )
  parser.add_argument(
    '--namespace',
    default='default',
    help='namespace to delete jobs from'
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

def parse_env(env):
  ''' parse and validate env vars '''
  # set this var if running locally
  # omit it if running inside a kubernetes cluster
  context = env.get('KUBECTL_CONTEXT', '')

  return context

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args(), parse_env(os.environ))
