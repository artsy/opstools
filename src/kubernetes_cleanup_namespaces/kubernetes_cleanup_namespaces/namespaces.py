import logging
import pytz

from datetime import datetime, timedelta
from dateutil.parser import parse as parsedatetime

from kubernetes_cleanup_namespaces.config import config
from kubernetes_cleanup_namespaces.kctl import Kctl

kctl = Kctl(config.context)

def cleanup_namespaces():
  ''' delete un-protected namespaces older than n days '''
  namespaces = kctl.get_namespaces()
  non_protected = non_protected_namespaces(namespaces)
  to_delete = old_namespaces(non_protected)
  delete_namespaces(to_delete)

def delete_namespaces(namespaces):
  ''' delete the given list of namespaces '''
  for ns in namespaces:
    delete_namespace(ns)
  logging.info("Done.")

def delete_namespace(namespace):
  ''' delete given namespace '''
  ns_name = namespace['metadata']['name']
  ns_created_at = namespace['metadata']['creationTimestamp']
  if config.force:
    logging.info(f"Deleting namespace {ns_name} created at {ns_created_at}")
    kctl.delete_namespace(ns_name)
  else:
    logging.info(f"Would have deleted namespace {ns_name} created at {ns_created_at}")

def non_protected_namespaces(namespaces):
  ''' given a list of namespaces, return those that are un-protected '''
  non_protected = [
    ns for ns in namespaces
      if not ns['metadata']['name'] in config.protected_namespaces
  ]
  return non_protected

def old_namespaces(namespaces):
  ''' given a list of namespaces, return those older than n days '''
  old = []
  for ns in namespaces:
    created_at = parsedatetime(ns['metadata']['creationTimestamp'])
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    if created_at < now - timedelta(days=config.ndays):
      old += [ns]
  return old
