import hvac
import logging

from lib.util import vault_string


class Vault:
  ''' Interface with Hashicorp Vault '''
  def __init__(self, addr, kvv2_mount_point, path, token):
    self.client = hvac.Client(
        url=addr,
        token=token
    )
    self.mount_point = kvv2_mount_point
    self._path = path

  def get(self, key):
    ''' get an entry '''
    full_path = f'{self._path}{key}'
    logging.debug(f'Vault: getting {full_path}')
    # if key does not exist or if data is soft-deleted, it raises:
    # hvac.exceptions.InvalidPath
    response = self.client.secrets.kv.read_secret_version(
      path=full_path,
      mount_point=self.mount_point
    )
    # return value of key
    value = response['data']['data'][key]
    return value

  def get_set(self, key, value):
    ''' set, but only if value is not there '''
    try:
      current_value = self.get(key)
    except:
      # any exception means there's no value
      self.set(key, value)
      return

    # no exception means there's some value
    if current_value == vault_string(value):
      logging.debug(f'{key} already has the value. Nothing to do.')
    else:
      self.set(key, value)

  def list(self):
    ''' list keys under a path '''
    logging.debug(f'Vault: listing {self._path}')
    # list includes soft-deleted keys
    response = self.client.secrets.kv.v2.list_secrets(
      path=self._path,
      mount_point=self.mount_point
    )
    return response

  def set(self, key, value):
    ''' set an entry '''
    full_path = f'{self._path}{key}'
    cleaned_value = vault_string(value)
    logging.debug(f'Vault: setting {full_path}')
    entry = { key: cleaned_value}
    response = self.client.secrets.kv.v2.create_or_update_secret(
      path=full_path,
      secret=entry,
      mount_point=self.mount_point,
    )
