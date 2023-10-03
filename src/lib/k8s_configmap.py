class ConfigMap:
  ''' Interface with one Kubernetes ConfigMap '''
  def __init__(self, kctl, namespace='default', name=None):
    self._kctl = kctl
    self.name = name
    self.namespace = namespace

  def get(self, var_name):
    ''' get value of one var in configmap '''
    data = self.load()
    return data[var_name]

  def load(self):
    ''' load all data of configmap '''
    data = self._kctl.get_configmap(self.name, self.namespace)
    return data['data']
