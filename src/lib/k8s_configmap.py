import json


class ConfigMap:
  def __init__(self, kctl, namespace='default', name=None):
    self._kctl = kctl
    self.namespace = namespace
    self.name = name

  def load(self):
    data = self._kctl.get_configmap(self.name, self.namespace)
    return data['data']

  def get(self, var_name):
    data = self.load()
    return data[var_name]
