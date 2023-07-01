from lib.date import over_ndays_ago

class Namespaces:
  ''' manage k8s namespaces data '''
  def __init__(self, kctl):
    # load namespaces data using the given kctl client
    self._kctl = kctl
    self._ns_data = kctl.get_namespaces()

  def created_at(self, namespace_name):
    ''' return creation time of the given namespace '''
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
      if over_ndays_ago(timestamp, ndays):
        name = ns['metadata']['name']
        names += [name]
    return names
