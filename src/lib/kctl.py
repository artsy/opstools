import logging
import json
import sys

from subprocess import check_output, SubprocessError

class Kctl():
  ''' interface with kubectl '''
  _timeout = 30 # seconds

  def __init__(self, context):
    logging.debug(f"Kctl > __init__: context: {context}")
    self._context = context

  def _run(self, command):
    ''' kubectl run the given command and return output '''
    if self._context is None:
      # when running in a pod inside kubernetes,
      # don't use kubeconfig or context
      # configure a service account with the permissions
      cmd = f"kubectl {command}"
    else:
      # when running locally
      cmd = f"kubectl --context {self._context} {command}"
    try:
      logging.debug(f"Kctl > _run: cmd: {cmd}")
      data = check_output(cmd, timeout=self._timeout, shell=True)
    except SubprocessError as e:
      logging.error(e)
      sys.exit(1)
    return data

  def delete_namespace(self, namespace):
    ''' delete given namespace '''
    cmd = f"delete namespace {namespace}"
    self._run(cmd)

  def get_namespaces(self):
    ''' return list of namespace objects '''
    cmd = "get namespaces -o json"
    output = self._run(cmd)
    data = json.loads(output)
    return data["items"]
