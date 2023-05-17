from datetime import datetime, timedelta

from lib.kctl import Kctl
from lib.logging import logging
from kubernetes_cleanup_pods_by_name.config import config

def cleanup_pods_by_name():
  """Cleanup pods by name older than NHOURS ago"""

  logging.info(
    "Cleaning up pods in {0} namespace " \
    "that are older than {1} hours " \
    "and contain '{2}' in their name"
    .format(config.namespace, config.nhours, config.name)
  )

  kctl = kctl_client()
  pods = kctl.get_pods(config.namespace)

  for pod in pods:
    pod_name = pod['metadata']['name']
    if config.name not in pod_name:
      logging.debug(
        f"Skipping pod {pod_name} because it does not contain '{config.name}' in its name"
      )
      continue

    if 'startTime' not in pod['status']:
      logging.debug(
        f"Skipping pod {pod_name} because it does not have a startTime"
      )
      continue

    pod_start_time = datetime.strptime(pod['status']['startTime'], "%Y-%m-%dT%H:%M:%SZ")

    if pod_start_time < datetime.utcnow() - timedelta(hours=config.nhours):
      if config.force:
        kctl.delete_pod(config.namespace, pod_name)
        logging.info(
          f"Deleted pod {pod_name}"
        )
      else:
        logging.info(
          f"Would have deleted pod {pod_name}"
        )

  logging.info("Done.")

def kctl_client():
  ''' instantiate a kctl client '''
  context = None
  if config.context:
    context = config.context
  return Kctl(context)
