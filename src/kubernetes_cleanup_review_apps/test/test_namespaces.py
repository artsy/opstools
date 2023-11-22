import kubernetes_cleanup_review_apps.cleanup

from kubernetes_cleanup_review_apps.cleanup import (
  config,
  delete_namespaces
)

from test.fixtures.namespaces import (
  mock_kctl_object,
  mock_ns_object
)

def describe_delete_namespaces():
  def describe_force_set():
    def it_calls_delete_namespace(mock_kctl_object, mock_ns_object, mocker):
      mocker.patch.object(config, 'force', True)
      delete_namespace_spy = mocker.spy(mock_kctl_object, 'delete_namespace')
      delete_namespaces(['ns1', 'ns2'], mock_ns_object)
      assert delete_namespace_spy.call_count == 2
      delete_namespace_spy.assert_has_calls([
        mocker.call('ns1'),
        mocker.call('ns2')
      ])
  def describe_force_unset():
    def it_does_not_call_delete_namespace(mock_kctl_object, mock_ns_object, mocker):
      mocker.patch.object(config, 'force', False)
      delete_namespace_spy = mocker.spy(mock_kctl_object, 'delete_namespace')
      delete_namespaces(['ns1', 'ns2'], mock_ns_object)
      assert delete_namespace_spy.call_count == 0
