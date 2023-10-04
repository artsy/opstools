import base64


class K8sSecret:
  ''' Interface with one K8S secret resource '''
  def __init__(self, kctl, namespace='default', name=None):
    self._kctl = kctl
    self.namespace = namespace
    self.name = name

  def get(self, var_name):
    data = self.load()
    value = data[var_name]
    return base64.b64decode(value).decode('utf8')

  def load(self):
    data = self._kctl.get_secret(self.name, self.namespace)
    return data['data']
