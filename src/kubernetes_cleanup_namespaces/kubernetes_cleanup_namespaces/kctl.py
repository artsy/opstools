import logging
import json
import sys

from subprocess import check_output, SubprocessError

from kubernetes_cleanup_namespaces.config import config

class Kctl():
  ''' interface with kubectl '''
  def __init__(self, context):
    self.context = context
    self.timeout = 5 # seconds

  def run(self, command):
    if self.context:
      # when running locally
      cmd = f"kubectl --context {self.context} {command}"
    else:
      # when running inside kubernetes, don't use kubeconfig or context
      # you will have to configure a service account and permissions for the pod
      cmd = f"kubectl {command}"
    try:
      logging.debug(cmd)
      data = json.loads(check_output(cmd, timeout=self.timeout, shell=True))
    except SubprocessError as e:
      logging.error(e)
      sys.exit(1)
    return data

kctl = Kctl(config.context)
