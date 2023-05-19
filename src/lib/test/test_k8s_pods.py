from dateutil.parser import parse as parsedatetime

from lib.test.fixtures.kctl import (
  mock_kctl,
  mock_kubectl_get_namespaces_json_object, # indirect usage
  mock_kubectl_get_pods_json_object
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
  def describe_delete():
    def it_calls_kctl_delete_pod(mock_kctl, mocker, pods_obj):
      kctl_spy = mocker.spy(mock_kctl, 'delete_pod')
      pods_obj.delete('pod1')
      assert kctl_spy.call_count == 1
      kctl_spy.assert_has_calls([
        mocker.call('foo', 'pod1')
      ])
  def describe_names():
    def it_returns_names_of_pods(pods_obj):
      assert pods_obj.names() == ['pod1', 'pod2']
  def describe_old_pods_names():
    def it_returns_old_pods(pods_obj):
      old_date = parsedatetime('2023-05-18T00:00:00Z')
      assert pods_obj.old_pods_names(old_date) == ['pod1']
