from kubernetes_cleanup_jobs.config import config

from kubernetes_cleanup_jobs.jobs import (
  cleanup_all_jobs,
  cleanup_completed_jobs,
  cleanup_jobs_by_name
)

if __name__ == "__main__":

  if config.name:
    cleanup_jobs_by_name()
  elif config.completed:
    cleanup_completed_jobs()
  elif config.all:
    cleanup_all_jobs()
