import argparse
import logging

import ecr_check_repos_for_terraform.context

from ecr_check_repos_for_terraform.check_repos import check
from lib.logging import setup_logging


def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
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
  loglevel = args.loglevel
  setup_logging(eval('logging.' + loglevel))

  logging.info(
    'Checking ECR for repositories that perhaps should be added to Terraform...'
  )
  repos = check()
  if len(repos) > 0:
    logging.info(f"Repositories found: {repos}")
    exit(1)
  else:
    logging.info("No repositories found.")
