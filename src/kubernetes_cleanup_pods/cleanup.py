# initialize the app
from kubernetes_cleanup_pods.config import config

from kubernetes_cleanup_pods.pods import (
  cleanup_pods
)

if __name__ == "__main__":

  cleanup_pods()
