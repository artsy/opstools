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
    if current_value == value:
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
