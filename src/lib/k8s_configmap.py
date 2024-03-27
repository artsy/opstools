import logging

from lib.util import match_dict_vars_by_value


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

class ConfigMaps:
  ''' Interface with all Kubernetes ConfigMaps '''
  def __init__(self, kctl, namespace='default'):
    self._kctl = kctl
    self._namespace = namespace

  def find_vars_by_value(self, match_function, *match_function_args):
    ''' scan configmaps var values and return vars matched by match_function '''
    matched_vars = {}
    for configmap_json in self._kctl.get_configmaps():
      configmap_name = configmap_json['metadata']['name']
      logging.debug(f'Scanning configmap {configmap_name}')
      if 'data' not in configmap_json:
        logging.debug(f'Configmap {configmap_name} has no data')
        continue
      matched_vars[configmap_name] = match_dict_vars_by_value(
        configmap_json['data'],
        match_function,
        *match_function_args
      )
    return matched_vars
