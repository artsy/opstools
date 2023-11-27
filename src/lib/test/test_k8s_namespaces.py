from lib.test.fixtures.kctl import (
  mock_kctl,
  mock_kubectl_get_namespaces_json_object,
  mock_kubectl_get_pods_json_object, # indirect usage
  mock_kubectl_get_jobs_json_object # indirect usage
)

from lib.k8s_namespaces import Namespaces

def describe_namespaces():
  def describe_instantiation():
    def it_stores_namespaces(mock_kubectl_get_namespaces_json_object, mock_kctl):
      obj = Namespaces(mock_kctl)
      assert obj._ns_data == mock_kubectl_get_namespaces_json_object['items']

  def describe_created_at():
    def it_returns_creation_time_when_namespace_exists(
      mock_kubectl_get_namespaces_json_object, mock_kctl
    ):
      obj = Namespaces(mock_kctl)
      ns1_timestamp = (
        mock_kubectl_get_namespaces_json_object['items'][0]['metadata']['creationTimestamp']
      )
      assert obj.created_at('namespace1') == ns1_timestamp
    def it_returns_none_when_namespace_does_not_exist(
      mock_kubectl_get_namespaces_json_object, mock_kctl
    ):
      obj = Namespaces(mock_kctl)
      assert obj.created_at('namespace10') is None

  def describe_delete():
    def it_calls_kctl_delete_namespace(mocker, mock_kctl):
      obj = Namespaces(mock_kctl)
      kctl_spy = mocker.spy(obj._kctl, 'delete_namespace')
      obj.delete('foonamespace')
      kctl_spy.assert_has_calls([mocker.call('foonamespace')])

  def describe_namespaces():
    def describe_no_labels_provided():
      def it_returns_all_namespaces(mock_kctl):
        obj = Namespaces(mock_kctl)
        names = obj.namespaces()
        assert names == ['namespace1', 'namespace2', 'namespace3']
    def describe_one_label_provided():
      def it_returns_matching_namespaces(mock_kctl):
        obj = Namespaces(mock_kctl)
        names = obj.namespaces(foo='bar')
        assert names == ['namespace1', 'namespace2']
      def it_returns_empty_when_no_namespace_matches(mock_kctl):
        obj = Namespaces(mock_kctl)
        names = obj.namespaces(foo='bing')
        assert names == []
      def it_converts_dashes_to_underscores(mock_kctl):
        obj = Namespaces(mock_kctl)
        names = obj.namespaces(foo_foo='bar')
        assert names == ['namespace3']
    def describe_multiple_labels_provided():
      def it_returns_matching_namespaces(mock_kctl):
        obj = Namespaces(mock_kctl)
        names = obj.namespaces(foo='bar', bar='baz')
        assert names == ['namespace1']

  def describe_old_namespaces():
    def it_returns_old_namespaces(mocker, mock_kctl):
      obj = Namespaces(mock_kctl)
      mocker.patch(
        'lib.k8s_namespaces.over_ndays_ago'
      ).side_effect = [True, False, False]
      names = obj.old_namespaces(10)
      assert names == ['namespace1']
