import logging
from datetime import datetime, timedelta

from lib.kctl import kctl_client
from kubernetes_cleanup_pods_by_name.config import config

def cleanup_pods_by_name():
  """Cleanup pods by name older than NHOURS ago"""

  logging.info(
    f"Cleaning up pods in {config.namespace} namespace "
    f"that are older than {config.nhours} hours "
    f"and contain '{config.name}' in their name"
  )

  kctl = kctl_client(config.context)
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
