import logging

from dateutil.parser import parse as parsedatetime

class Jobs:
  ''' manage jobs data '''
  def __init__(self, kctl, namespace):
    self._jobs_data = kctl.get_jobs(namespace)
    self._kctl = kctl
    self._namespace = namespace

  def delete(self, job_name):
    ''' delete a given job '''
    self._kctl.delete_job(self._namespace, job_name)

  def names(self):
    ''' return names of jobs '''
    return [
      job['metadata']['name'] for job in self._jobs_data
    ]

  def completed_jobs_names(self):
    ''' return names of completed jobs '''
    job_names = []
    for job in self._jobs_data:
      job_name = job['metadata']['name']
      if 'succeeded' not in job['status']:
        logging.debug(f"job {job_name} has not completed")
        continue
      job_names += [job_name]
    return job_names

  def old_jobs_names(self, old_date, incomplete=False):
    ''' return names of jobs that started before old_date.
        by default, only completed jobs are considered '''
    job_names = []
    for job in self._jobs_data:
      job_name = job['metadata']['name']
      if not incomplete:
        if 'completionTime' not in job['status']:
          logging.debug(f"job {job_name} has no completionTime")
          continue
        timestamp = job['status']['completionTime']
      else:
        if 'startTime' not in job['status']:
          logging.debug(f"job {job_name} has no startTime")
          continue
        timestamp = job['status']['startTime']
      job_time = parsedatetime(timestamp)
      if job_time < old_date:
        job_names += [job_name]
    return job_names
