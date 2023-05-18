import os
import argparse

# add /src to sys.path for importing modules in 'lib' dir
# an alternative to having to add context.py to every module
# https://stackoverflow.com/a/4383597
import sys
sys.path.insert(1, os.path.abspath(__file__ + '/../../..'))

from lib.logging import *

class AppConfig:
  def __init__(self, cmdline_args, env):
    ''' set app-wide configs and initialize the app '''
    name, nhours, namespace, force, loglevel = (
      cmdline_args.name,
      int(cmdline_args.nhours),
      cmdline_args.namespace,
      cmdline_args.force,
      cmdline_args.loglevel,
    )

    context = env

    self.name = name
    self.nhours = nhours
    self.namespace = namespace
    self.force = force
    self.context = context

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
    'name',
    help='delete pods with this name'
  )
  parser.add_argument(
    'nhours',
    help='delete pods older than n hours'
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

def parse_env(env):
  ''' parse and validate env vars '''
  # set this var if running locally
  # omit it if running inside a kubernetes cluster
  context = env.get('KUBECTL_CONTEXT', '')

  return context

# import this from main script
# object will be instantiated only once
config = AppConfig(parse_args(), parse_env(os.environ))
