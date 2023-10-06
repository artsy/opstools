from lib.k8s_secret import K8sSecret
from lib.test.fixtures.kctl import (
  mock_kctl,
  mock_kubectl_get_namespaces_json_object, # indirect usage
  mock_kubectl_get_pods_json_object, # indirect usage
  mock_kubectl_get_jobs_json_object # indirect usage
)


def describe_k8s_secret():
  def describe_init():
    def it_inits(mock_kctl):
      obj = K8sSecret(mock_kctl, 'foosecret')
      assert obj._kctl is mock_kctl
      assert obj._name == 'foosecret'
      assert obj._namespace == 'default'

  def describe_get():
    def it_gets(mocker, mock_kctl):
      obj = K8sSecret(mock_kctl, 'foosecret')
      mocker.patch.object(obj, 'load', return_value={'foo': 'YmFy'})
      assert obj.get('foo') == 'bar'

  def describe_load():
    def it_loads(mocker, mock_kctl):
      obj = K8sSecret(mock_kctl, 'foosecret')
      assert obj.load() == 'foodata'
