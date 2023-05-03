import logging
import json
import sys

from subprocess import check_output, SubprocessError

class Kctl():
  ''' interface with kubectl '''
  _self = None # track the singleton instance
  _context = None
  _timeout = 5 # seconds

  def __new__(cls, context):
    # allow one instantiation only (singleton use case)
    if cls._self is None:
      cls._self = super().__new__(cls)
      cls._context = context
    return cls._self

  @classmethod
  def _run(cls, command):
    ''' kubectl run the given command and return output '''
    if cls._context:
      # when running locally
      cmd = f"kubectl --context {cls._context} {command}"
    else:
      # when running inside kubernetes, don't use kubeconfig or context
      # you will have to configure a service account and permissions for the pod
      cmd = f"kubectl {command}"
    try:
      logging.debug(cmd)
      data = check_output(cmd, timeout=cls._timeout, shell=True)
    except SubprocessError as e:
      logging.error(e)
      sys.exit(1)
    return data

  @classmethod
  def delete_namespace(cls, namespace):
    ''' delete given namespace '''
    cmd = f"delete namespace {namespace}"
    cls._run(cmd)

  @classmethod
  def get_namespaces(cls):
    ''' return list of namespace objects '''
    cmd = "get namespaces -o json"
    data = json.loads(cls._run(cmd))
    return data["items"]
