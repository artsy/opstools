import logging

import kubernetes_cleanup_pods.context

from kubernetes_cleanup_pods.config import config

from lib.k8s_pods import Pods
from lib.kctl import Kctl
from lib.util import list_intersect

def cleanup_pods():
  ''' delete pods that match age, name, and completion status '''
  logging.info(
    f"Deleting pods that are older than {config.nhours} hours."
  )
  kctl = Kctl(config.in_cluster, config.artsy_env)
  pods_obj = Pods(kctl, config.namespace)
  to_delete_pods = pods_obj.old_pods(config.nhours)
  if config.completed:
    logging.info(
      f"Limiting deletion to only completed pods."
    )
    completed_pods = pods_obj.completed_pods()
    to_delete_pods = list_intersect(to_delete_pods, completed_pods)
  if config.name:
    logging.info(
      f"Limiting deletion to only pods whose names contain {config.name}."
    )
    name_matched_pods = pods_obj.pods_with_name(config.name)
    to_delete_pods = list_intersect(to_delete_pods, name_matched_pods)
  delete_pods(to_delete_pods, pods_obj)
  logging.info("Done deleting pods.")

def delete_pods(pod_names, pods_obj):
  ''' delete the given list of pods '''
  # prevent accidentally deleting all pods of a k8s cluster!
  if len(pod_names) > 30:
    raise Exception(f"Deleting more than 30 pods not allowed.")
  for pod in pod_names:
    if config.force:
      pods_obj.delete(pod)
      logging.info(f"Deleted pod {pod}")
    else:
      logging.info(f"Would have deleted pod {pod}")
