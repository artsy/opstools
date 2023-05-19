#!/usr/bin/env python

# initialize the app
from kubernetes_cleanup.config import config

from kubernetes_cleanup.pods import (
  cleanup_pods_by_name,
  cleanup_completed_pods,
)

if __name__ == "__main__":

  if config.completed:
    cleanup_completed_pods()
  elif config.name:
    cleanup_pods_by_name()
