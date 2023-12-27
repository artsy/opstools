import os
import sys

import kubernetes_cleanup_jobs.context

from lib.test.fixtures.k8s_jobs import jobs_obj
from lib.test.fixtures.kctl import (
  mock_kctl, # indirect usage
  mock_kubectl_get_namespaces_json_object, # indirect usage
  mock_kubectl_get_pods_json_object, # indirect usage
  mock_kubectl_get_jobs_json_object # indirect usage
)

from kubernetes_cleanup_jobs.jobs import delete_jobs

def describe_delete_jobs():
  def describe_force_set():
    def it_calls_jobs_obj_delete(mocker, jobs_obj):
      delete_spy = mocker.spy(jobs_obj, 'delete')
      delete_jobs(['job1', 'job2'], jobs_obj, True)
      assert delete_spy.call_count == 2
      delete_spy.assert_has_calls([
        mocker.call('job1'),
        mocker.call('job2')
      ])
  def describe_force_unset():
    def it_does_not_call_jobs_obj_delete(mocker, jobs_obj):
      delete_spy = mocker.spy(jobs_obj, 'delete')
      delete_jobs(['job1', 'job2'], jobs_obj, False)
      assert delete_spy.call_count == 0
