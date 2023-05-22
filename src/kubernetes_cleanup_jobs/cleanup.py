#!/usr/bin/env python

from kubernetes_cleanup_jobs.config import config

from kubernetes_cleanup_jobs.jobs import (
  cleanup_jobs,
  cleanup_completed_jobs,
)

if __name__ == "__main__":

  if config.incomplete:
    cleanup_jobs()
  else:
    cleanup_completed_jobs()
