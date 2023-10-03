import hvac
import logging
import os

from lib.util import vault_version, unquote


class Vault:
  ''' interface with hashicorp vault client '''
  def __init__(self, artsy_project, artsy_env):
    env_var_name = f'{artsy_env.upper()}_VAULT_ADDR'
    vault_addr = os.environ.get(env_var_name)
    self.client = hvac.Client(
        url=vault_addr,
        token=os.environ.get('VAULT_TOKEN')
    )
    self.mount_point = os.environ.get('VAULT_KVV2_MOUNT_POINT')
    prefix = 'kubernetes/apps/'
    self._path = f'{prefix}{artsy_project}/'

  def get(self, key):
    ''' get an entry '''
    full_path = f'{self._path}{key}'
    logging.debug(f'Vault: getting {full_path}')
    # if key does not exist or if data is soft-deleted:
    # raise exceptions.VaultError.from_status(hvac.exceptions.InvalidPath
    response = self.client.secrets.kv.read_secret_version(
      path=full_path,
      mount_point=self.mount_point
    )
    # return value of key
    value = response['data']['data'][key]
    return value

  def get_set(self, key, value):
    ''' set only if current version doesn't exist or has a different value '''
    try:
      current_value = self.get(key)
    except:
      # any exception means there's no value
      self.set(key, value)
      return

    # no exception means there's some value
    if current_value == vault_version(value):
      logging.debug(f'{var} already has the value. Nothing to do.')
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
    cleaned_value = vault_version(value)
    logging.debug(f'Vault: setting {full_path}')
    entry = { key: cleaned_value}
    response = self.client.secrets.kv.v2.create_or_update_secret(
      path=full_path,
      secret=entry,
      mount_point=self.mount_point,
    )
