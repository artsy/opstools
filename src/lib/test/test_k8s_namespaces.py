from dateutil.parser import parse as parsedatetime

from lib.k8s_namespaces import \
  Namespaces

# mock_kctl is used by namespaces_obj fixture,
# but must be imported here 
from lib.test.fixtures.kctl import \
  mock_kctl, \
  mock_kubectl_get_namespaces_json_object

from lib.test.fixtures.k8s_namespaces import \
  namespaces_obj as ns

def describe_namespaces():
  def describe_instantiation():
    def it_stores_namespaces(mock_kubectl_get_namespaces_json_object, ns):
      assert ns._ns_data == mock_kubectl_get_namespaces_json_object['items']
  def describe_created_at():
    def it_returns_creation_time_when_namespace_exists(
      mock_kubectl_get_namespaces_json_object, ns
    ):
      ns1_timestamp = mock_kubectl_get_namespaces_json_object['items'][0]['metadata']['creationTimestamp']
      assert ns.created_at('namespace1') == parsedatetime(ns1_timestamp)
    def it_returns_none_when_namespace_does_not_exist(
      mock_kubectl_get_namespaces_json_object, ns
    ):
      assert ns.created_at('namespace10') is None
  def describe_names():
    def it_returns_names_of_namespaces(ns):
      assert ns.names() == ['namespace1', 'namespace2']
