import logging
import json
import sys

from subprocess import check_output, SubprocessError

class Kctl:
  ''' interface with kubectl '''
  def __init__(self, in_cluster, context):
    logging.debug(f"Kctl > __init__: in_cluster: {in_cluster}, context: {context}")
    self._in_cluster = in_cluster
    self._context = context

  def _run(self, command, timeout=30):
    ''' kubectl run the given command and return output '''
    if self._in_cluster:
      # when running in a pod inside kubernetes,
      # don't use kubeconfig or context
      # configure a service account with the permissions
      cmd = f"kubectl {command}"
    else:
      # when running locally
      cmd = f"kubectl --context {self._context} {command}"
    try:
      logging.debug(f"Kctl > _run: cmd: {cmd}")
      data = check_output(cmd, timeout=timeout, shell=True)
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

  def get_pods(self, namespace):
    ''' return a list of pod objects '''
    cmd = f"get pods -n {namespace} -o json"
    output = self._run(cmd)
    data = json.loads(output)
    if not data["items"]:
      logging.debug(f"Kctl > get_pods: no pods found in namespace: {namespace}")
    return data["items"]

  def delete_pod(self, namespace, pod_name):
    ''' delete a given pod in a given namespace '''
    cmd = f"delete pod {pod_name} -n {namespace}"
    self._run(cmd, timeout=90)

  def get_jobs(self, namespace):
    ''' return a list of job objects '''
    cmd = f"get jobs -n {namespace} -o json"
    output = self._run(cmd)
    data = json.loads(output)
    if not data["items"]:
      logging.debug(f"Kctl > get_jobs: no jobs found in namespace: {namespace}")
    return data["items"]

  def delete_job(self, namespace, job_name):
    ''' delete a given job in a given namespace '''
    cmd = f"delete job {job_name} -n {namespace}"
    self._run(cmd, timeout=90)

  def get_default_namespace_objects(self, type, output_format):
    ''' get objects of type, from default namespace '''
    return self.get_objects('default', type, output_format)

  def get_objects(self, namespace, type, output_format):
    ''' get objects of type, from namespace '''
    cmd = f"get {type} -o {output_format} -n {namespace}"
    output = self._run(cmd)
    return output
