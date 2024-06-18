from lib.k8s_configmap import ConfigMap
from lib.test.fixtures.kctl import (
  mock_kctl,
  mock_kubectl_get_namespaces_json_object, # indirect usage
  mock_kubectl_get_pods_json_object, # indirect usage
  mock_kubectl_get_jobs_json_object # indirect usage
)

def describe_configmap():
  def describe_init():
    def it_inits(mock_kctl):
      obj = ConfigMap(mock_kctl, 'fooconfigmap')
      assert obj._kctl is mock_kctl
      assert obj._name == 'fooconfigmap'
      assert obj._namespace == 'default'

  def describe_get():
    def it_gets(mocker, mock_kctl):
      obj = ConfigMap(mock_kctl, 'fooconfigmap')
      mocker.patch.object(obj, 'load', return_value={'foo': 'bar'})
      assert obj.get('foo') == 'bar'

  def describe_load():
    def it_returns_data_when_there_is_data(mocker, mock_kctl):
      mock_kctl_obj = mock_kctl
      configmap_obj = ConfigMap(mock_kctl_obj, 'fooconfigmap')
      data = {
        'data': 'foodata'
      }
      mocker.patch.object(mock_kctl_obj, 'get_configmap', return_value=data)
      assert configmap_obj.load() == 'foodata'
    def it_returns_empty_dict_when_there_is_no_data(mocker, mock_kctl):
      mock_kctl_obj = mock_kctl
      configmap_obj = ConfigMap(mock_kctl_obj, 'fooconfigmap')
      mocker.patch.object(mock_kctl_obj, 'get_configmap', return_value={'foo': 'bar'})
      assert configmap_obj.load() == {}
