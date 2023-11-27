from lib.date import over_ndays_ago
from lib.util import (
  dict1_in_dict2,
  replace_dashes_in_dict_keys_with_underscores
)


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

  def namespaces(self, **kwargs):
    '''
    return names of namespaces,
    if labels (e.g. foo=bar, bar=baz) are specified in kwargs,
    return only namespaces that have all the specified labels,
    dashes in label keys received from Kubernetes are converted to underscores.
    '''
    if kwargs:
      return [
        ns['metadata']['name']
        for ns in self._ns_data
        if 'labels' in ns['metadata'] and
        dict1_in_dict2(
          kwargs,
          replace_dashes_in_dict_keys_with_underscores(
            ns['metadata']['labels']
          )
        )
      ]
    else:
      # no labels specified, return all
      return [ns['metadata']['name'] for ns in self._ns_data]

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
