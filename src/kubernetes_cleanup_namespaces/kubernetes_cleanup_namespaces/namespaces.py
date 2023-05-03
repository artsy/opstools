import logging

import kubernetes_cleanup_namespaces.context
from lib.date import older_than_ndays
from lib.k8s_namespaces import Namespaces
from lib.kctl import Kctl
from lib.util import list_subtract

from kubernetes_cleanup_namespaces.config import config

def cleanup_namespaces():
  ''' delete unprotected namespaces older than n days '''
  kctl = kctl_client()
  ns_obj = Namespaces(kctl)
  namespaces = ns_obj.names()
  unprotected = unprotected_namespaces(namespaces)
  to_delete = old_namespaces(unprotected, ns_obj)
  delete_namespaces(to_delete, ns_obj, kctl)

def delete_namespaces(namespaces, ns_obj, kctl):
  ''' delete the given list of namespaces '''
  for name in namespaces:
    created_at = ns_obj.created_at(name)
    if config.force:
      logging.info(f"Deleting namespace {name} created at {created_at}")
      kctl.delete_namespace(name)
    else:
      logging.info(f"Would have deleted namespace {name} created at {created_at}")
  logging.info("Done.")

def kctl_client():
  ''' instantiate a kctl client '''
  context = None
  if config.context:
    context = config.context
  return Kctl(context)

def unprotected_namespaces(namespaces):
  ''' given a list of namespaces, return those that are unprotected '''
  return list_subtract(namespaces, config.protected_namespaces)

def old_namespaces(namespaces, ns_obj):
  ''' given a list of namespaces, return those older than n days '''
  old = []
  for name in namespaces:
    created_at = ns_obj.created_at(name)
    if older_than_ndays(created_at, config.ndays):
      old += [name]
  return old
