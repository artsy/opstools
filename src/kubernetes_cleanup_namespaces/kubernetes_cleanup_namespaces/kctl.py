import json

from subprocess import check_output

from kubernetes_cleanup_namespaces.config import config

class Kctl():
  ''' interface with kubectl '''
  def __init__(self, context):
    self.context = context

  def run(self, command):
    if self.context:
      # when running locally
      cmd = f"kubectl --context {self.context} {command}"
    else:
      # when running inside kubernetes, don't use kubeconfig or context
      # you will have to configure a service account and permissions for the pod
      cmd = f"kubectl {command}"
    data = json.loads(check_output(cmd, shell=True))
    return data

kctl = Kctl(config.context)
