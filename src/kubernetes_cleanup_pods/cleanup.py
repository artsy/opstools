# initialize the app
from kubernetes_cleanup_pods.config import config

from kubernetes_cleanup_pods.pods import (
  cleanup_completed_pods,
  cleanup_pods_by_name
)

if __name__ == "__main__":

  if config.completed:
    cleanup_completed_pods()
  elif config.name:
    cleanup_pods_by_name()
