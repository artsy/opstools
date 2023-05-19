#!/usr/bin/env python

# initialize the app
from kubernetes_cleanup_jobs.config import config

from kubernetes_cleanup_jobs.jobs import (
  cleanup_completed_jobs,
)

if __name__ == "__main__":

  if config.nhours:
    cleanup_completed_jobs()
