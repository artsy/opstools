#!/usr/bin/env python

# initialize the app
from kubernetes_cleanup_pods_by_name.config import config

from kubernetes_cleanup_pods_by_name.pods_by_name import (
  cleanup_pods_by_name
)

if __name__ == "__main__":

  cleanup_pods_by_name()
