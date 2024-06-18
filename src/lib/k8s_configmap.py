class ConfigMap:
  ''' Interface with one Kubernetes ConfigMap '''
  def __init__(self, kctl, name, namespace='default'):
    self._kctl = kctl
    self._name = name
    self._namespace = namespace

  def get(self, var_name):
    ''' get value of one var in configmap '''
    data = self.load()
    return data[var_name]

  def load(self):
    ''' load all data of configmap '''
    data = self._kctl.get_configmap(self._name, self._namespace)
    if 'data' in data:
      return data['data']
    else:
      return {}
