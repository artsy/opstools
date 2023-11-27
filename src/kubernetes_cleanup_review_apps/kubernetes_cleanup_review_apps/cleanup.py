import logging

import kubernetes_cleanup_review_apps.context

from lib.k8s_namespaces import Namespaces
from lib.kctl import Kctl
from lib.util import list_intersect


def cleanup_review_apps(ndays, force, in_cluster):
  ''' delete review apps older than n days '''
  logging.info(
    f"Deleting review apps older than {ndays} days"
  )
  kctl = Kctl(in_cluster, 'staging')
  ns_obj = Namespaces(kctl)
  # delete review apps by deleting their namespaces
  review_app_namespaces = ns_obj.namespaces(app_phase='review')
  old_namespaces = ns_obj.old_namespaces(ndays)
  to_delete = list_intersect(review_app_namespaces, old_namespaces)
  delete_namespaces(to_delete, ns_obj, force)
  logging.info(
    f"Done deleting namespaces."
  )

def delete_namespaces(namespaces, ns_obj, force):
  ''' delete the given list of namespaces '''
  for ns in namespaces:
    created_at = ns_obj.created_at(ns)
    if force:
      logging.info(
        f"Deleting {ns} created at {created_at}"
      )
      ns_obj.delete(ns)
    else:
      logging.info(
        f"Would have deleted namespace {ns} created at {created_at}"
      )
