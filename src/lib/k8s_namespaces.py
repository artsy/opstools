class Namespaces:
  ''' manage k8s namespaces data '''
  def __init__(self, kctl):
    # load namespaces data using the given kctl client
    self._kctl = kctl
    self._ns_data = kctl.get_namespaces()

  def created_at(self, namespace_name):
    ''' given the name of a namespace, return its creation time '''
    for ns in self._ns_data:
      if ns['metadata']['name'] == namespace_name:
        timestamp = ns['metadata']['creationTimestamp']
        return timestamp

  def delete(self, namespace_name):
    ''' delete the given namespace '''
    self._kctl.delete_namespace(namespace_name)

  def old_namespaces(self, ndays):
    ''' return names of namespaces older than ndays '''
    names = []
    for ns in self._ns_data:
      # utc with timezone info
      timestamp = ns['metadata']['creationTimestamp']
      if older_than_ndays(timestamp, ndays):
        name = ns['metadata']['name']
        names += [name]
    return names
