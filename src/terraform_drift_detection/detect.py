#!/usr/bin/env python

import logging

from terraform_drift_detection.init import init
from terraform_drift_detection.terraform import check_repos
from terraform_drift_detection.util import Drift

init()
if Drift.DRIFT in check_repos():
  logging.error('Drift detected.')
  exit(1)
