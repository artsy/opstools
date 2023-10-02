import json

import pdb

class ConfigMap:
  def __init__(self, kctl, namespace='default', name=None):
    self._kctl = kctl
    self.namespace = namespace
    self.name = name

  def load(self):
    data = self._kctl.get_configmap(self.name, self.namespace)
    return data['data']
