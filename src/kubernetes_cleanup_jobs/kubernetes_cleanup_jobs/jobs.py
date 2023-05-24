import logging

from lib.k8s_jobs import Jobs
from lib.date import date_nhours_ago
from lib.kctl import kctl_client
from lib.util import list_intersect

from kubernetes_cleanup_jobs.config import config

def cleanup_jobs_by_name():
  logging.info('Not implemented yet.')

def cleanup_all_jobs():
  ''' cleanup jobs older than NHOURS.
      this includes jobs that are still running! '''
  logging.info(
    f"Cleaning up jobs older than {config.nhours} hours in {config.namespace} namespace"
  )
  kctl = kctl_client(config.context)
  jobs_obj = Jobs(kctl, config.namespace)
  job_names = jobs_obj.names()
  old_datetime = date_nhours_ago(config.nhours)
  age_matched_jobs = jobs_obj.old_jobs_names(old_datetime, True) # include running jobs
  to_delete_jobs = list_intersect(job_names, age_matched_jobs)
  delete_jobs(to_delete_jobs, jobs_obj)
  logging.info("Done.")

def cleanup_completed_jobs():
  ''' cleanup completed jobs older than NHOURS '''
  logging.info(
    f"Cleaning up completed jobs older than {config.nhours} hours in {config.namespace} namespace"
  )
  kctl = kctl_client(config.context)
  jobs_obj = Jobs(kctl, config.namespace)
  job_names = jobs_obj.completed_jobs_names()
  old_datetime = date_nhours_ago(config.nhours)
  age_matched_jobs = jobs_obj.old_jobs_names(old_datetime)
  to_delete_jobs = list_intersect(job_names, age_matched_jobs)
  delete_jobs(to_delete_jobs, jobs_obj)
  logging.info("Done.")

def delete_jobs(job_names, jobs_obj):
  ''' delete the given list of jobs '''
  for job in job_names:
    if config.force:
      jobs_obj.delete(job)
      logging.info(f"Deleted job {job}")
    else:
      logging.info(f"Would have deleted job {job}")
