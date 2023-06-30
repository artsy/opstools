import logging

import kubernetes_cleanup_jobs.context

from kubernetes_cleanup_jobs.config import config

from lib.k8s_jobs import Jobs
from lib.kctl import Kctl

def cleanup_jobs():
  '''
  delete jobs older than nhours,
  even those that are still running!
  '''
  logging.info(
    f"Deleting jobs older than {config.nhours} hours " +
    f"in {config.namespace} namespace"
  )
  kctl = Kctl(config.in_cluster, config.artsy_env)
  jobs_obj = Jobs(kctl, config.namespace)
  old_jobs = jobs_obj.old_jobs(config.nhours)
  delete_jobs(old_jobs, jobs_obj)
  logging.info("Deleted jobs.")

def delete_jobs(job_names, jobs_obj):
  ''' delete the given list of jobs '''
  for job in job_names:
    if config.force:
      logging.info(f"Deleting job {job} ...")
      jobs_obj.delete(job)
    else:
      logging.info(f"Would have deleted job {job}")
