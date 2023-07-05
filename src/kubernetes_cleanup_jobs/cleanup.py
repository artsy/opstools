from kubernetes_cleanup_jobs.config import config

from kubernetes_cleanup_jobs.jobs import (
  cleanup_jobs
)

if __name__ == "__main__":

  cleanup_jobs()
