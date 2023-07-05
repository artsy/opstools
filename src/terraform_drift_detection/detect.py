import logging

# initialize the app
from terraform_drift_detection.config import config

from terraform_drift_detection.terraform import (
  check_repos,
  Drift
)

if __name__ == "__main__":

  if Drift.DRIFT in check_repos():
    logging.error('Drift detected.')
    exit(1)
