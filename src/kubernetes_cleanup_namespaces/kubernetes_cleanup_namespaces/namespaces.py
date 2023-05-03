import logging

from dateutil.parser import parse as parsedatetime

import kubernetes_cleanup_namespaces.context
from lib.date import older_than_ndays
from lib.kctl import Kctl
from lib.util import list_subtract

from kubernetes_cleanup_namespaces.config import config

class Namespaces():
  ''' manage namespaces data '''
  def __init__(self, kctl):
    # load namespaces data using the given kctl client
    self._ns_data = kctl.get_namespaces()

  def created_at(self, namespace_name):
    ''' given the name of a namespace, return its creation time '''
    for ns in self._ns_data:
      if ns['metadata']['name'] == namespace_name:
        timestamp = ns['metadata']['creationTimestamp']
        return parsedatetime(timestamp)

  def names(self):
    ''' return names of namespaces '''
    return [
      ns['metadata']['name'] for ns in self._ns_data
    ]

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
  return Kctl(config.context)

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
