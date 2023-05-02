import logging
import pytz

from datetime import datetime, timedelta
from dateutil.parser import parse as parsedatetime

from kubernetes_cleanup_namespaces.config import config
from kubernetes_cleanup_namespaces.kctl import kctl

def cleanup_namespaces():
  ''' delete un-protected namespaces older than n days '''
  namespaces = get_ns()
  non_protected =  non_protected_ns(namespaces)
  to_delete = old_ns(non_protected)
  delete_ns(to_delete)

def delete_ns(namespaces):
  ''' delete the given list of namespaces '''
  for ns in namespaces:
    ns_name = ns['metadata']['name']
    ns_created_at = ns['metadata']['creationTimestamp']
    if config.force:
      logging.info(f"Deleting namespace {ns_name} created at {ns_created_at}")
      data = kctl.run(f"delete namespace {ns_name}")
    else:
      logging.info(f"Would have deleted namespace {ns_name} created at {ns_created_at}")
  logging.info("Done.")

def get_ns():
  ''' return list of namespaces '''
  data = kctl.run("get namespaces -o json")
  return data["items"]

def non_protected_ns(namespaces):
  ''' given a list of namespaces, return those that are un-protected '''
  non_protected = [
    ns for ns in namespaces
      if not ns['metadata']['name'] in config.protected_namespaces
  ]
  return non_protected

def old_ns(namespaces):
  ''' given a list of namespaces, return those older than n days '''
  old = []
  for ns in namespaces:
    created_at = parsedatetime(ns['metadata']['creationTimestamp'])
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    if created_at < now - timedelta(days=config.ndays):
      old += [ns]
  return old
