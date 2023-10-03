import base64
import json


class K8sSecret:
  def __init__(self, kctl, namespace='default', name=None):
    self._kctl = kctl
    self.namespace = namespace
    self.name = name

  def load(self):
    data = self._kctl.get_secret(self.name, self.namespace)
    return data['data']

  def get(self, var_name):
    data = self.load()
    value = data[var_name]
    return base64.b64decode(value).decode('utf8')
