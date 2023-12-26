import logging

import kubernetes_cleanup_pods.context

from lib.k8s_pods import Pods
from lib.kctl import Kctl
from lib.util import list_intersect

def cleanup_pods(
  artsy_env,
  completed,
  force,
  in_cluster,
  name,
  namespace,
  nhours
):
  ''' delete pods that match age, name, and completion status '''
  logging.info(
    f"Deleting pods that are older than {nhours} hours."
  )
  kctl = Kctl(in_cluster, artsy_env)
  pods_obj = Pods(kctl, namespace)
  to_delete_pods = pods_obj.old_pods(nhours)
  if completed:
    logging.info(
      f"Limiting deletion to only completed pods."
    )
    completed_pods = pods_obj.completed_pods()
    to_delete_pods = list_intersect(to_delete_pods, completed_pods)
  if name:
    logging.info(
      f"Limiting deletion to only pods whose names contain {name}."
    )
    name_matched_pods = pods_obj.pods_with_name(name)
    to_delete_pods = list_intersect(to_delete_pods, name_matched_pods)
  delete_pods(to_delete_pods, pods_obj, force)
  logging.info("Done deleting pods.")

def delete_pods(pod_names, pods_obj, force):
  ''' delete the given list of pods '''
  # prevent accidentally deleting all pods of a k8s cluster!
  if len(pod_names) > 30:
    raise Exception(f"Deleting more than 30 pods not allowed.")
  for pod in pod_names:
    if force:
      pods_obj.delete(pod)
      logging.info(f"Deleted pod {pod}")
    else:
      logging.info(f"Would have deleted pod {pod}")
