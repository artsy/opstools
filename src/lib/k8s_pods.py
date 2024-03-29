import logging

from lib.date import over_nhours_ago

class Pods:
  ''' manage k8s pods data for a namespace '''
  def __init__(self, kctl, namespace):
    self._kctl = kctl
    self._namespace = namespace
    self._pods_data = kctl.get_pods(namespace)

  def completed_pods(self):
    ''' return names of completed pods '''
    pod_names = []
    for pod in self._pods_data:
      pod_name = pod['metadata']['name']
      if 'phase' not in pod['status']:
        logging.debug(f"Skipping {pod_name} as it has no phase.")
        continue
      if pod['status']['phase'] == 'Succeeded':
        pod_names += [pod_name]
    return pod_names

  def delete(self, pod_name):
    ''' delete the given pod '''
    self._kctl.delete_pod(pod_name, self._namespace)

  def old_pods(self, nhours):
    ''' return names of pods that started before nhours ago '''
    pod_names = []
    for pod in self._pods_data:
      pod_name = pod['metadata']['name']
      if 'startTime' not in pod['status']:
        logging.debug(f"Skipping {pod_name} as it has no startTime.")
        continue
      # utc with timezone info
      timestamp = pod['status']['startTime']
      if over_nhours_ago(timestamp, nhours):
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
