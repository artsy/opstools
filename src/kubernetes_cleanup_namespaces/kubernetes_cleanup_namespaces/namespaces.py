from dateutil.parser import parse as parsedatetime

from datetime import datetime, timedelta

from kubernetes_cleanup_namespaces.kctl import kctl
from kubernetes_cleanup_namespaces.kctl import config

import logging
import json
import pytz

def compile_namespaces():
  ''' get all namespaces '''
  data = kctl.run("get namespaces -o json")
  namespaces = []
  for namespace in data["items"]:
    namespaces += [namespace]
  return namespaces

def delete_namespaces(namespaces):
  for ns in namespaces:
    ns_name = ns['metadata']['name']
    ns_created_at = ns['metadata']['creationTimestamp']
    if config.force:
      logging.info(f"Deleting namespace {ns_name} created at {ns_created_at}")
      data = kctl.run(f"delete namespace {ns_name}")
    else:
      logging.info(f"Would have deleted namespace {ns_name} created at {ns_created_at}")
  logging.info("Done.")

def non_protected_namespaces(list):
  ''' given list of namespaces, return same list excluding protected namespaces '''
  PROTECTED_NAMESPACES = [
    'cert-manager',
    'data-application',
    'default',
    'ingress-nginx',
    'kube-node-lease',
    'kube-public',
    'kubernetes-dashboard',
    'kube-system'
  ]
  non_protected = []
  for ns in list:
    ns_name = ns['metadata']['name']
    if ns_name in PROTECTED_NAMESPACES:
      continue
    else:
      non_protected += [ns]
  return non_protected

def too_old_namespaces(namespaces):
  too_old = []
  for ns in namespaces:
    created_at = parsedatetime(ns['metadata']['creationTimestamp'])
    now = datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)
    if created_at < now - timedelta(days=config.ndays):
      too_old += [ns]
  return too_old

def cleanup_namespaces():
  ''' delete namespaces older than n days '''
  namespaces = compile_namespaces()
  non_protected =  non_protected_namespaces(namespaces)
  to_delete = too_old_namespaces(non_protected)
  delete_namespaces(to_delete)
