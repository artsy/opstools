import logging
import json
import sys

from subprocess import check_output, SubprocessError

class Kctl:
  ''' interface with kubectl '''
  def __init__(self, in_cluster, context):
    self._in_cluster = in_cluster
    self._context = context

  def _run(self, command, timeout=30):
    ''' return output of the given kubectl command '''
    if self._in_cluster:
      # being run inside kubernetes cluster
      # don't use kubeconfig or context
      # rely on pod's service account to have permissions
      cmd = f"kubectl {command}"
    else:
      # being run outside kubernetes cluster, specify context
      cmd = f"kubectl --context {self._context} {command}"
    try:
      logging.debug(f"Kctl: running kubectl cmd: {cmd}")
      output = check_output(cmd, timeout=timeout, shell=True)
    except SubprocessError as e:
      logging.error(e)
      sys.exit(1)
    return output

  def delete_job(self, job_name, namespace='default'):
    ''' delete the given job in the given namespace '''
    self.delete_namespaced_object('job', job_name, namespace)

  def delete_namespace(self, namespace):
    ''' delete given namespace '''
    cmd = f"delete namespace {namespace}"
    self._run(cmd)

  def delete_namespaced_object(self, type, name, namespace):
    ''' delete the given object in the given namespace '''
    cmd = f"-n {namespace} delete {type} {name}"
    self._run(cmd, timeout=90)

  def delete_pod(self, pod_name, namespace='default'):
    ''' delete the given pod in the given namespace '''
    self.delete_namespaced_object('pod', pod_name, namespace)

  def get_jobs(self, namespace='default'):
    ''' return jobs in the given namespace'''
    output = self.get_namespaced_object('jobs', 'json', namespace)
    data = json.loads(output)
    if not data["items"]:
      logging.debug(f"Kctl: no jobs found in {namespace} namespace.")
    return data["items"]

  def get_namespaced_object(self, type, output_format, namespace):
    ''' return objects of the given type in the given namespace '''
    cmd = f"-n {namespace} get {type} -o {output_format}"
    output = self._run(cmd)
    return output

  def get_namespaces(self):
    ''' return namespaces '''
    cmd = "get namespaces -o json"
    output = self._run(cmd)
    data = json.loads(output)
    return data["items"]

  def get_pods(self, namespace='default'):
    ''' return pods in the given namespace '''
    output = self.get_namespaced_objects('pods', 'json', namespace)
    data = json.loads(output)
    if not data["items"]:
      logging.debug(f"Kctl: no pods found in {namespace} namespace.")
    return data["items"]
