import boto3
import hvac
import logging


class Vault:
  ''' Interface with Hashicorp Vault '''
  def __init__(
    self,
    addr,
    auth_method,
    token=None,
    role=None,
    kvv2_mount_point=None,
    path=None,
    sanitizer=None
  ):
    self._client = hvac.Client(url=addr)
    self._mount_point = kvv2_mount_point
    self._path = path
    # a function for sanitizing a value before setting it in Vault
    # this is org-specific
    self._sanitizer = sanitizer
    self.login(self._client, auth_method, token, role)

  def login(self, client, auth_method, token=None, role=None):
    ''' log into Vault using the specified method '''
    if auth_method == 'iam':
      self.iam_login(role)
    elif auth_method == 'token':
      self._client.token = token
    else:
      raise Exception(f'Un-supported auth method: {auth_method}')

  def iam_login(self, role):
    ''' log into Vault using AWS IAM keys '''
    session = boto3.Session()
    credentials = session.get_credentials()
    self._client.auth.aws.iam_login(
      credentials.access_key,
      credentials.secret_key,
      credentials.token,
      role=role
    )

  def get(self, key):
    ''' get an entry '''
    full_path = f'{self._path}{key}'
    logging.debug(f'Vault: getting {full_path}')
    # if key does not exist or if data is soft-deleted, it raises:
    # hvac.exceptions.InvalidPath
    response = self._client.secrets.kv.read_secret_version(
      path=full_path,
      mount_point=self._mount_point
    )
    # return value of key
    value = response['data']['data'][key]
    return value

  def get_set(self, key, value, dry_run=False):
    ''' set, but only if value is not there '''
    try:
      current_value = self.get(key)
    except:
      # any exception means there's no value
      self.set(key, value, dry_run)
      return

    # no exception means there's some value
    if current_value == self._sanitizer(value):
      logging.debug(
        f'{key} already has the value. Nothing to do.'
      )
    else:
      self.set(key, value, dry_run)

  def list(self):
    ''' list keys under a path '''
    logging.debug(f'Vault: listing {self._path}')
    # list includes soft-deleted keys
    response = self._client.secrets.kv.v2.list_secrets(
      path=self._path,
      mount_point=self._mount_point
    )
    return response

  def set(self, key, value, dry_run=False):
    ''' set an entry '''
    full_path = f'{self._path}{key}'
    cleaned_value = self._sanitizer(value)
    logging.debug(f'Vault: setting {full_path}')
    entry = { key: cleaned_value}
    if dry_run:
      logging.info(f'Would have set {full_path}')
    else:
      response = self._client.secrets.kv.v2.create_or_update_secret(
        path=full_path,
        secret=entry,
        mount_point=self._mount_point,
      )

  def take_snapshot(self, output_file):
    binary_response = self._client.sys.take_raft_snapshot()
    with open(output_file, 'wb') as f:
      f.write(binary_response.content)

