import logging
import json
import sys

from subprocess import check_output, SubprocessError

from kubernetes_cleanup_namespaces.config import config

class Kctl():
  ''' interface with kubectl '''
  _self = None # faciliate singleton use case
  _context = None
  _timeout = 5 # seconds

  def __new__(cls, context):
    if cls._self is None:
      cls._self = super().__new__(cls)
      cls._context = context
    return cls._self

  def run(self, command):
    if self._context:
      # when running locally
      cmd = f"kubectl --context {self._context} {command}"
    else:
      # when running inside kubernetes, don't use kubeconfig or context
      # you will have to configure a service account and permissions for the pod
      cmd = f"kubectl {command}"
    try:
      logging.debug(cmd)
      data = json.loads(check_output(cmd, timeout=self._timeout, shell=True))
    except SubprocessError as e:
      logging.error(e)
      sys.exit(1)
    return data

  def delete_namespace(self, namespace):
    ''' delete given namespace '''
    cmd = f"delete namespace {namespace}"
    self.run(cmd)

  def get_namespaces(self):
    ''' return list of namespaces '''
    cmd = "get namespaces -o json"
    data = self.run(cmd)
    return data["items"]
