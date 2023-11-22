import argparse
import logging
import os

import migrate_config_secrets.context

from kubernetes_cleanup_review_apps.namespaces import (
  cleanup_namespaces
)

if __name__ == "__main__":

  cleanup_namespaces()
