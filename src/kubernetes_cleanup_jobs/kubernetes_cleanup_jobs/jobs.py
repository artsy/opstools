import logging

import kubernetes_cleanup_jobs.context

from kubernetes_cleanup_jobs.config import config

from lib.date import date_nhours_ago
from lib.k8s_jobs import Jobs
from lib.kctl import Kctl
from lib.util import list_intersect

def cleanup_jobs_by_name():
  logging.info('Not implemented yet.')

def cleanup_all_jobs():
  '''
  delete jobs older than nhours,
  even those that are still running!
  '''
  logging.info(
    f"Deleting jobs older than {config.nhours} hours " +
    f"in {config.namespace} namespace""
  )
  kctl = Kctl(config.in_cluster, config.artsy_env)
  jobs_obj = Jobs(kctl, config.namespace)
  all_jobs = jobs_obj.names()
  old_datetime = date_nhours_ago(config.nhours)
  old_jobs = jobs_obj.old_jobs_names(
    old_datetime, incomplete=True
  ) # include incomplete jobs
  to_delete_jobs = list_intersect(all_jobs, age_matched_jobs)
  delete_jobs(to_delete_jobs, jobs_obj)
  logging.info("Done deleting jobs.")

def cleanup_completed_jobs():
  ''' cleanup completed jobs older than nhours '''
  logging.info(
    f"Deleting completed jobs older than {config.nhours} " +
    f"hours in {config.namespace} namespace"
  )
  kctl = Kctl(config.in_cluster, config.artsy_env)
  jobs_obj = Jobs(kctl, config.namespace)
  completed_jobs = jobs_obj.completed_jobs_names()
  old_datetime = date_nhours_ago(config.nhours)
  old_jobs = jobs_obj.old_jobs_names(old_datetime)
  to_delete_jobs = list_intersect(completed_jobs, old_jobs)
  delete_jobs(to_delete_jobs, jobs_obj)
  logging.info("Done deleting jobs.")

def delete_jobs(job_names, jobs_obj):
  ''' delete the given list of jobs '''
  for job in job_names:
    if config.force:
      jobs_obj.delete(job)
      logging.info(f"Deleted job {job}")
    else:
      logging.info(f"Would have deleted job {job}")
