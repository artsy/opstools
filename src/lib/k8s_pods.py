import logging

from dateutil.parser import parse as parsedatetime

class Pods:
  ''' manage pods data '''
  def __init__(self, kctl, namespace):
    self._pods_data = kctl.get_pods(namespace)
    self._kctl = kctl
    self._namespace = namespace

  def delete(self, pod_name):
    ''' delete the given pod '''
    self._kctl.delete_pod(self._namespace, pod_name)

  def names(self):
    ''' return names of pods'''
    return [
      pod['metadata']['name'] for pod in self._pods_data
    ]

  def completed_pods_names(self):
    ''' return names of completed pods '''
    pod_names = []
    for pod in self._pods_data:
      pod_name = pod['metadata']['name']
      if 'phase' not in pod['status']:
        logging.debug(f"pod {pod_name} has no phase")
        continue
      if pod['status']['phase'] == 'Succeeded':
        pod_names += [pod_name]
    return pod_names

  def old_pods_names(self, old_date):
    ''' return names of pods that started before old_date '''
    pod_names = []
    for pod in self._pods_data:
      pod_name = pod['metadata']['name']
      if 'startTime' not in pod['status']:
        logging.debug(f"pod {pod_name} has no startTime")
        continue
      timestamp = pod['status']['startTime']
      pod_start_time = parsedatetime(timestamp)
      if pod_start_time < old_date:
        pod_names += [pod_name]
    return pod_names
