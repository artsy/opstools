import logging

from lib.date import date_nhours_ago
from lib.k8s_pods import Pods
from lib.kctl import kctl_client
from lib.util import list_intersect, list_match_str

from kubernetes_cleanup_pods.config import config

def cleanup_pods_by_name():
  """Cleanup pods by name older than NHOURS ago"""
  logging.info(
    f"Cleaning up pods in {config.namespace} namespace "
    f"that are older than {config.nhours} hours "
    f"and contain '{config.name}' in their name"
  )
  kctl = kctl_client(config.context)
  pods_obj = Pods(kctl, config.namespace)
  pod_names = pods_obj.names()
  name_matched_pods = list_match_str(pod_names, config.name)
  old_datetime = date_nhours_ago(config.nhours)
  age_matched_pods = pods_obj.old_pods_names(old_datetime)
  to_delete_pods = list_intersect(
    name_matched_pods, age_matched_pods
  )
  delete_pods(to_delete_pods, pods_obj)
  logging.info("Done.")

def cleanup_completed_pods():
  """Cleanup completed pods older than NHOURS ago"""
  logging.info(
    f"Cleaning up completed pods in {config.namespace} namespace"
  )
  kctl = kctl_client(config.context)
  pods_obj = Pods(kctl, config.namespace)
  pod_names = pods_obj.completed_pods_names()
  old_datetime = date_nhours_ago(config.nhours)
  age_matched_pods = pods_obj.old_pods_names(old_datetime)
  to_delete_pods = list_intersect(pod_names, age_matched_pods)
  delete_pods(to_delete_pods, pods_obj)
  logging.info("Done.")

def delete_pods(pod_names, pods_obj):
  ''' delete the given list of pods '''
  for pod in pod_names:
    if config.force:
      pods_obj.delete(pod)
      logging.info(f"Deleted pod {pod}")
    else:
      logging.info(f"Would have deleted pod {pod}")
