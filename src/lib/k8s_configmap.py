import logging

class ConfigMap:
  ''' Interface with one Kubernetes ConfigMap '''
  def __init__(self, kctl, name, namespace='default'):
    self._kctl = kctl
    self._name = name # of configmap
    self._namespace = namespace

  def get(self, var_name):
    ''' get value of one var in configmap '''
    data = self.load()
    return data[var_name]

  def load(self):
    ''' load all data of configmap '''
    data = self._kctl.get_configmap(self._name, self._namespace)
    return data['data']

def match(data, match_function, *args):
  return [
    key for key, value in data.items()
    if match_function(value, *args)
  ]

class ConfigMaps:
  ''' Interface with all Kubernetes ConfigMaps '''
  def __init__(self, kctl, namespace='default'):
    self._kctl = kctl
    self._namespace = namespace

  def scan(self, match_function, *args):
    ''' scan configmaps and return names of vars matched '''
    matched_vars = {}
    for configmap in self._kctl.get_configmaps():
      configmap_name = configmap['metadata']['name']
      logging.info(f'Scanning configmap {configmap_name}')
      if 'data' not in configmap:
        continue
      matched_vars[configmap_name] = match(configmap['data'], match_function, *args)
    return matched_vars
