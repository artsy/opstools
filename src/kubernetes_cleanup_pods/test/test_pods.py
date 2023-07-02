import os
import pytest
import sys

import kubernetes_cleanup_pods.context

from lib.test.fixtures.k8s_pods import pods_obj
from lib.test.fixtures.kctl import (
  mock_kctl, # indirect usage
  mock_kubectl_get_namespaces_json_object, # indirect usage
  mock_kubectl_get_pods_json_object, # indirect usage
  mock_kubectl_get_jobs_json_object # indirect usage
)

from kubernetes_cleanup_pods.pods import (
  config,
  delete_pods
)

def describe_delete_pods():
  def describe_force_set():
    def it_calls_pods_obj_delete(mocker, pods_obj):
      mocker.patch.object(config, 'force', True)
      delete_spy = mocker.spy(pods_obj, 'delete')
      delete_pods(['pod1', 'pod2'], pods_obj)
      assert delete_spy.call_count == 2
      delete_spy.assert_has_calls([
        mocker.call('pod1'),
        mocker.call('pod2')
      ])
    def it_refuses_to_delete_more_than_30_pods(mocker, pods_obj):
      mocker.patch.object(config, 'force', True)
      with pytest.raises(Exception):
        delete_pods(['pod']*31, pods_obj)

  def describe_force_unset():
    def it_does_not_call_pods_obj_delete(mocker, pods_obj):
      mocker.patch.object(config, 'force', False)
      delete_spy = mocker.spy(pods_obj, 'delete')
      delete_pods(['pod1', 'pod2'], pods_obj)
      assert delete_spy.call_count == 0
