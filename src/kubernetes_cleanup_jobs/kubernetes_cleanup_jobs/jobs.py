import logging

import kubernetes_cleanup_jobs.context

from lib.k8s_jobs import Jobs
from lib.kctl import Kctl

def cleanup_jobs(
  loglevel,
  artsy_env,
  force,
  in_cluster,
  namespace,
  nhours
):
  '''
  delete jobs older than nhours,
  even those that are still running!
  '''
  logging.info(
    f"Deleting jobs older than {nhours} hours " +
    f"in {namespace} namespace"
  )
  kctl = Kctl(in_cluster, artsy_env)
  jobs_obj = Jobs(kctl, namespace)
  old_jobs = jobs_obj.old_jobs(nhours)
  delete_jobs(old_jobs, jobs_obj, force)
  logging.info("Deleted jobs.")

def delete_jobs(job_names, jobs_obj, force):
  ''' delete the given list of jobs '''
  for job in job_names:
    if force:
      logging.info(f"Deleting {job} ...")
      jobs_obj.delete(job)
    else:
      logging.info(f"Would have deleted job {job}")
