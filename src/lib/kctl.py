import logging
import json
import sys

from subprocess import run, check_output, SubprocessError

from lib.util import error_exit

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
    logging.debug(f"Kctl: running kubectl cmd: {cmd}")
    # exception not raised if cmd fails
    resp = run(
      cmd,
      capture_output=True,
      shell=True,
      text=True,
      timeout=timeout
    )
    return resp

  def delete_job(self, job_name, namespace='default'):
    ''' delete the given job in the given namespace '''
    self.delete_namespaced_object('job', job_name, namespace)

  def delete_namespace(self, namespace):
    ''' delete given namespace '''
    cmd = f"delete namespace {namespace}"
    resp = self._run(cmd)
    if resp.returncode != 0:
      error_exit(
        f"Command failed: {cmd}\n" +
        f"Stderr from Command: {resp.stderr}"
      )

  def delete_namespaced_object(self, type, name, namespace):
    ''' delete the given object in the given namespace '''
    cmd = f"-n {namespace} delete {type} {name}"
    resp = self._run(cmd, timeout=90)
    if resp.returncode != 0:
      logging.warning(f"Command failed: {cmd}")
      # ignore 'not found' errors
      if 'not found' in resp.stderr:
        logging.info(f"Ignoring error from command: {resp.stderr}")
      else:
        error_exit(f"Stderr from Command: {resp.stderr}")

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
    resp = self._run(cmd)
    # get should always succeed
    if resp.returncode != 0:
      error_exit(
        f"Command failed: {cmd}\n" +
        f"Stderr from Command: {resp.stderr}"
      )
    return resp.stdout

  def get_namespaces(self):
    ''' return namespaces '''
    cmd = "get namespaces -o json"
    resp = self._run(cmd)
    data = json.loads(resp.stdout)
    return data["items"]

  def get_pods(self, namespace='default'):
    ''' return pods in the given namespace '''
    output = self.get_namespaced_object('pods', 'json', namespace)
    data = json.loads(output)
    if not data["items"]:
      logging.debug(f"Kctl: no pods found in {namespace} namespace.")
    return data["items"]
