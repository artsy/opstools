from dateutil.parser import parse as parsedatetime

class Namespaces():
  ''' manage namespaces data '''
  def __init__(self, kctl):
    # load namespaces data using the given kctl client
    self._ns_data = kctl.get_namespaces()

  def created_at(self, namespace_name):
    ''' given the name of a namespace, return its creation time '''
    for ns in self._ns_data:
      if ns['metadata']['name'] == namespace_name:
        timestamp = ns['metadata']['creationTimestamp']
        return parsedatetime(timestamp)

  def names(self):
    ''' return names of namespaces '''
    return [
      ns['metadata']['name'] for ns in self._ns_data
    ]
