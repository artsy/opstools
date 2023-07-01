from lib.test.fixtures.kctl import (
  mock_kctl,
  mock_kubectl_get_namespaces_json_object, # indirect usage
  mock_kubectl_get_pods_json_object,
  mock_kubectl_get_jobs_json_object # indirect usage
)

from lib.test.fixtures.k8s_pods import pods_obj

def describe_pods():

  def describe_instantiation():
    def it_stores_data(
      mock_kctl,
      mock_kubectl_get_pods_json_object,
      pods_obj
    ):
      assert pods_obj._kctl is mock_kctl
      assert pods_obj._namespace == 'foo'
      assert pods_obj._pods_data == mock_kubectl_get_pods_json_object['items']

  def describe_completed_pods():
    def it_returns_completed_pods(pods_obj):
      assert pods_obj.completed_pods() == ['pod2']

  def describe_delete():
    def it_calls_kctl_delete_pod(mock_kctl, mocker, pods_obj):
      kctl_spy = mocker.spy(mock_kctl, 'delete_pod')
      pods_obj.delete('pod1')
      assert kctl_spy.call_count == 1
      kctl_spy.assert_has_calls([
        mocker.call('pod1', 'foo')
      ])

  def describe_old_pods():
    def it_returns_old_pods(pods_obj, mocker):
      mocker.patch(
        'lib.k8s_pods.over_nhours_ago'
      ).side_effect = [True, False]
      assert pods_obj.old_pods(10) == ['pod1']

  def describe_pods_with_names():
    def it_returns_the_right_pods(pods_obj):
      pods = pods_obj.pods_with_name('2')
      assert pods == ['pod2']
