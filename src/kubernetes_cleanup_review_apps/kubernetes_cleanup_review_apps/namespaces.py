import logging

import kubernetes_cleanup_review_apps.context

from kubernetes_cleanup_review_apps.config import config

from lib.k8s_namespaces import Namespaces
from lib.kctl import Kctl
from lib.util import list_subtract

def cleanup_namespaces():
  ''' delete unprotected namespaces older than n days '''
  logging.info(
    f"Deleting namespaces older than {config.ndays} days"
  )
  kctl = Kctl(config.in_cluster, config.artsy_env)
  ns_obj = Namespaces(kctl)
  old_namespaces = ns_obj.old_namespaces(config.ndays)
  to_delete = list_subtract(old_namespaces, config.protected_namespaces)
  delete_namespaces(to_delete, ns_obj)
  logging.info(
    f"Done deleting namespaces."
  )

def delete_namespaces(namespaces, ns_obj):
  ''' delete the given list of namespaces '''
  for ns in namespaces:
    created_at = ns_obj.created_at(ns)
    if config.force:
      logging.info(
        f"Deleting {ns} created at {created_at}"
      )
      ns_obj.delete(ns)
    else:
      logging.info(
        f"Would have deleted namespace {ns} created at {created_at}"
      )
