import logging

from lib.date import older_than_nhours

class Jobs:
  ''' manage Kubernetes jobs data from a given namespace '''
  def __init__(self, kctl, namespace):
    self._jobs_data = kctl.get_jobs(namespace)
    self._kctl = kctl
    self._namespace = namespace

  def delete(self, job_name):
    ''' delete the given job '''
    self._kctl.delete_job(job_name, self._namespace)

  def old_jobs(self, nhours):
    ''' return names of jobs that started before nhours ago '''
    job_names = []
    for job in self._jobs_data:
      # skip jobs that oddly have no startTime
      if 'startTime' not in job['status']:
        logging.debug(f"Skipping {job_name} as it has no startTime")
        continue
      # utc with timezone info
      timestamp = job['status']['startTime']
      if older_than_nhours(timestamp, nhours):
        job_name = job['metadata']['name']
        job_names += [job_name]
    return job_names
