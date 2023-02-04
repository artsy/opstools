#!/usr/bin/env python

import logging

from terraform_drift_detection.terraform import check_repos
from terraform_drift_detection.util import Drift, setup_logging

setup_logging()
results = check_repos()
if Drift.DRIFT in results:
  logging.error('Drift detected.')
  exit(1)
