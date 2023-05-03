import logging
import pytz

from datetime import datetime, timedelta
from dateutil.parser import parse as parsedatetime

from kubernetes_cleanup_namespaces.config import config
from lib.kctl import Kctl

kctl = Kctl(config.context)

def cleanup_namespaces():
  ''' delete unprotected namespaces older than n days '''
  namespaces = kctl.get_namespaces()
  unprotected = unprotected_namespaces(namespaces)
  to_delete = old_namespaces(unprotected)
  delete_namespaces(to_delete)

def delete_namespace(namespace):
  ''' delete the given namespace '''
  ns_name = namespace['metadata']['name']
  ns_created_at = namespace['metadata']['creationTimestamp']
  if config.force:
    logging.info(f"Deleting namespace {ns_name} created at {ns_created_at}")
    kctl.delete_namespace(ns_name)
  else:
    logging.info(f"Would have deleted namespace {ns_name} created at {ns_created_at}")

def delete_namespaces(namespaces):
  ''' delete the given list of namespaces '''
  for ns in namespaces:
    delete_namespace(ns)
  logging.info("Done.")

def unprotected_namespaces(namespaces):
  ''' given a list of namespaces, return those that are unprotected '''
  unprotected = [
    ns for ns in namespaces
      if not ns['metadata']['name'] in config.protected_namespaces
  ]
  return unprotected

def old_namespaces(namespaces):
  ''' given a list of namespaces, return those older than n days '''
  old = []
  for ns in namespaces:
    ns_timestamp = ns['metadata']['creationTimestamp']
    ns_created_at = parsedatetime(ns_timestamp)
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=pytz.utc)
    ndays_ago_date = now_utc - timedelta(days=config.ndays)
    if ns_created_at < ndays_ago_date:
      old += [ns]
  return old
