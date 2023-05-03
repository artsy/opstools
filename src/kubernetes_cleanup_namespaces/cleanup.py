#!/usr/bin/env python

# initialize the app
from kubernetes_cleanup_namespaces.config import config

from kubernetes_cleanup_namespaces.namespaces import cleanup_namespaces

if __name__ == "__main__":

  cleanup_namespaces()
