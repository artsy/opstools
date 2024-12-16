import boto3
import hvac
import logging

from hvac.api.auth_methods import Kubernetes

from lib.export_backup import write_file


class Vault:
  ''' Interface with Hashicorp Vault '''
  def __init__(
    self,
    addr,
    auth_method,
    token=None,
    role=None,
    kvv2_mount_point=None,
    path=None
  ):
    self._client = hvac.Client(url=addr)
    self._mount_point = kvv2_mount_point
    self._path = path
    self._login(auth_method, token, role)

  ## login methods

  def _login(self, auth_method, token=None, role=None):
    ''' log into Vault using the specified method '''
    if auth_method == 'iam':
      self._iam_login(role)
    elif auth_method == 'token':
      self._client.token = token
    elif auth_method == 'kubernetes':
      self._kubernetes_login(role)
    else:
      raise Exception(f'Un-supported auth method: {auth_method}')

  def _kubernetes_login(self, role=None):
    ''' authenticate using k8s pod service account token '''
    with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as token_file:
      jwt = token_file.read()
    Kubernetes(self._client.adapter).login(role=role, jwt=jwt)

  def _iam_login(self, role=None):
    ''' log into Vault using AWS IAM keys '''
    session = boto3.Session()
    credentials = session.get_credentials()
    if role == None:
      # role not specified, let hvac default role to same as iam username
      self._client.auth.aws.iam_login(
        credentials.access_key,
        credentials.secret_key,
        credentials.token,
      )
    else:
      self._client.auth.aws.iam_login(
        credentials.access_key,
        credentials.secret_key,
        credentials.token,
        role=role
      )

  ## other methods

  def get(self, key):
    ''' get an entry '''
    full_path = f'{self._path}{key}'
    logging.debug(f'Vault: getting {full_path}')
    # read_secret_version raises hvac.exceptions.InvalidPath if:
    # - key doesn't exist
    # - deletion_time is set in key's meta
    # - destroyed is set to True in key's meta
    #
    # when key has multiple versions,
    # by default, read_secret_version reads the latest.
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
    if current_value == value:
      logging.debug(
        f'{key} already has the value. Nothing to do.'
      )
    else:
      self.set(key, value, dry_run)

  def is_valid(self, key):
    '''
    return True if current version of secret is valid
    valid means the version is not soft-deleted nor destroyed
    '''
    valid = True
    meta = self.read_meta(key)
    current_version = str(
      meta['data']['current_version']
    )
    # a string and it's either null or a timestamp
    # a timestamp means the version is soft deleted at that time
    deletion_time = meta['data']['versions'][current_version]['deletion_time']
    # either True or False
    destroyed = meta['data']['versions'][current_version]['destroyed']
    if deletion_time != '':
      logging.debug(
        f'Version {current_version} of {key} is deleted at {deletion_time}.'
      )
      valid = False
    if destroyed:
      logging.debug(
        f'Version {current_version} of {key} is destroyed.'
      )
      valid = False
    return valid

  def list(
    self,
    only_valid=True,
    match_function=None,
    match_type=None
  ):
    ''' list keys under a path '''
    logging.debug(f'Vault: listing {self._path}')
    keys = []
    response = self._client.secrets.kv.v2.list_secrets(
      path=self._path,
      mount_point=self._mount_point
    )
    keys = response['data']['keys']
    if only_valid:
      keys = [
        key for key in keys
        if self.is_valid(key)
      ]
    if match_function is not None:
        if match_type == 'key':
          keys = [
            key for key in keys
            if match_function(key)
          ]
        elif match_type == 'value':
          keys = [
            key for key in keys
            if match_function(self.get(key))
          ]
        else:
          raise Exception(
            f'Un-supported match type: {match_type}'
          )
    return keys

  def read_custom_meta(self, key):
    ''' return custom metadata of secret '''
    full_path = f'{self._path}{key}'
    meta = self.read_meta(key)
    if 'custom_metadata' in meta['data']:
      return meta['data']['custom_metadata']
    return None

  def read_meta(self, key):
    ''' return metadata of secret '''
    full_path = f'{self._path}{key}'
    meta = self._client.secrets.kv.v2.read_secret_metadata(
      path=full_path,
      mount_point=self._mount_point
    )
    logging.debug(f'Current meta: {meta}')
    return meta

  def set(self, key, value, dry_run=False):
    ''' set an entry '''
    full_path = f'{self._path}{key}'
    logging.debug(f'Vault: setting {full_path}')
    entry = { key: value}
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
    write_file(output_file, binary_response.content, data_format='binary')

  def update_custom_meta(self, key, meta_key, meta_value):
    ''' update an entry's custom metadata '''
    full_path = f'{self._path}{key}'
    # get current meta first so as not to overwrite the whole thing
    current_custom_meta = self.read_custom_meta(key)
    logging.debug(f'Current custom meta: {current_custom_meta}')
    if current_custom_meta is None:
      current_custom_meta = {}
    current_custom_meta[meta_key] = meta_value
    logging.debug(f'Vault: setting {full_path} custom metadata {meta_key}')
    # this overwrites all custom metadata
    self._client.secrets.kv.v2.update_metadata(
      path=full_path,
      mount_point=self._mount_point,
      custom_metadata=current_custom_meta
    )
