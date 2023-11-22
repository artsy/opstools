import argparse
import logging
import os

import migrate_config_secrets.context

from kubernetes_cleanup_review_apps.cleanup import (
  cleanup_review_apps
)

if __name__ == "__main__":

  cleanup_review_apps()
