#!/usr/bin/env python

import os
import sys

import argparse
import logging
import json

import kubernetes_cleanup_namespaces.context
from lib.logging import setup_logging

from subprocess import check_output, CalledProcessError

from dateutil.parser import parse as parsedatetime

from datetime import datetime, timedelta

import pytz

def parse_args():
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument(
    'ndays',
    help='delete namespaces older than n days'
  )
  parser.add_argument(
    '--force',
    action='store_true',
    help='to actually delete'
  )
  parser.add_argument(
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  return parser.parse_args()

def get_env():
  ''' get vars from env '''
  # set this if running locally
  context = os.environ.get('KUBECTL_CONTEXT', '')

  # set this if running inside kubernetes
  k8s_cluster = os.environ.get('K8S_CLUSTER', '')

  return context, k8s_cluster

def validate(context, k8s_cluster):
  ''' validate params obtained from env and command line '''
  if not context and not k8s_cluster:
    sys.exit(
      "Error: either KUBECTL_CONTEXT or K8S_CLUSTER must be specified in the environment"
    )

  if context and k8s_cluster:
    sys.exit(
      "Error: KUBECTL_CONTEXT and K8S_CLUSTER must not both be specified in the environment"
    )

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

def compile_namespaces():
  ''' get all namespaces '''
  if context:
    # when running locally
    cmd = f"kubectl --context {context} get namespaces -o json"
  else:
    # when running inside kubernetes, don't use kubeconfig or context
    # you will have to configure a service account and permissions for the pod
    cmd = f"kubectl get namespaces -o json"
  data = json.loads(check_output(cmd, shell=True))
  namespaces = []
  for namespace in data["items"]:
    namespaces += [namespace]
  return namespaces

def too_old_namespaces(namespaces, ndays):
  too_old = []
  for ns in namespaces:
    created_at = parsedatetime(ns['metadata']['creationTimestamp'])
    now = datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)
    if created_at < now - timedelta(days=ndays):
      too_old += [ns]
  return too_old

def delete_namespaces(namespaces, force):
  for ns in namespaces:
    ns_name = ns['metadata']['name']
    ns_created_at = ns['metadata']['creationTimestamp']
    if force:
      logging.info(f"Deleting namespace {ns_name} created at {ns_created_at}")
      cmd = f"kubectl --context {context} delete namespace {ns_name}"
    else:
      logging.info(f"Would have deleted namespace {ns_name} created at {ns_created_at}")
  logging.info("Done.")

if __name__ == "__main__":

  args = parse_args()
  force, loglevel, ndays = args.force, args.loglevel, int(args.ndays)

  setup_logging(eval('logging.' + loglevel))

  context, k8s_cluster = get_env()

  validate(context, k8s_cluster)

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

  namespaces = compile_namespaces()
  non_protected_namespaces =  non_protected_namespaces(namespaces)
  to_delete_namespaces = too_old_namespaces(non_protected_namespaces, ndays)
  delete_namespaces(to_delete_namespaces, force)
