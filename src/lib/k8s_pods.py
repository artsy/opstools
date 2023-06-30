import logging

from dateutil.parser import parse as parsedatetime

from lib.date import date_nhours_ago

class Pods:
  ''' manage pods data '''
  def __init__(self, kctl, namespace):
    self._pods_data = kctl.get_pods(namespace)
    self._kctl = kctl
    self._namespace = namespace

  def completed_pods(self):
    ''' return names of completed pods '''
    pod_names = []
    for pod in self._pods_data:
      pod_name = pod['metadata']['name']
      if 'phase' not in pod['status']:
        logging.debug(f"Skipping pod {pod_name} as it has no phase")
        continue
      if pod['status']['phase'] == 'Succeeded':
        pod_names += [pod_name]
    return pod_names

  def delete(self, pod_name):
    ''' delete the given pod '''
    self._kctl.delete_pod(self._namespace, pod_name)

  def old_pods(self, nhours):
    ''' return names of pods that started before nhours ago '''
    pod_names = []
    for pod in self._pods_data:
      pod_name = pod['metadata']['name']
      if 'startTime' not in pod['status']:
        logging.debug(f"Skipping pod {pod_name} as it has no startTime")
        continue
      timestamp = pod['status']['startTime']
      start_time = parsedatetime(timestamp)
      old_date = date_nhours_ago(config.nhours)
      if start_time < old_date:
        pod_names += [pod_name]
    return pod_names

  def pods_with_name(self, str1):
    ''' return names of pods whose names contain str1 string '''
    pod_names = []
    for pod in self._pods_data:
      pod_name = pod['metadata']['name']
      if str1 in pod_name:
        pod_names += [pod_name]
    return pod_names
