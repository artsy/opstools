import hvac
import logging
import os

from subprocess import run as subprocess_run


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

  def _run(self, command, timeout=30, expect_success=False):
    ''' run command using vault and return result '''
    cmd = f"vault {command}"
    logging.debug(f"Vault: running {cmd}")
    # exception not raised if run fails
    resp = subprocess_run(
      cmd,
      capture_output=True,
      shell=True,
      text=True,
      timeout=timeout
    )
    if expect_success and resp.returncode != 0:
      raise Exception(
        f"Command failed: {command}\n" +
        f"Stderr from Command: {resp.stderr}"
      )
    return resp

  def set(self, key, value):
    ''' set an entry '''
    full_path = f'{self._path}{key}'
    self.validate(value)
    cleaned_value = self.clean_value(value)
    logging.debug(f'Vault: setting {full_path}')
    entry = { key: cleaned_value}
    response = self.client.secrets.kv.v2.create_or_update_secret(
      path=full_path,
      secret=entry,
      mount_point=self.mount_point,
    )

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
    return self.unquote(value)

  def is_quoted(self, value):
    ''' decide whether value is quoted '''
    # double quote
    if value[0] == '"' and value[-1] == '"':
      return '"'
    # single quote
    elif value[0] == "'" and value[1] == "'":
      return "'"

  def unquote(self, value):
    quote_type = self.is_quoted(value)
    if quote_type:
      return value.strip(quote_type)
    return value

  def list(self):
    ''' list keys under a path '''
    logging.debug(f'Vault: listing {self._path}')
    # list includes soft-deleted keys
    response = self.client.secrets.kv.v2.list_secrets(
      path=self._path,
      mount_point=self.mount_point
    )
    return response

  def validate(self, value_string):
    # do not allow values to be quoted
    quotes = ["'", '"']
    if value_string[0] in quotes:
      logging.error('Quoted values not accepted')
      raise
    if value_string[-1] in quotes:
      logging.error('Quoted values not accepted')
      raise

  def clean_value(self, value_string):
    '''
    double quote strings that contain special YAML characters,
    such as asterisk,
    otherwise ESO won't be able to parse
    '''
    special_chars = ['*']
    for char in special_chars:
      if char in value_string:
        return f'"{value_string}"'
    return value_string
