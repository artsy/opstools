import logging
import os

import hvac

import load_secrets_from_vault.context

from lib.util import (
  url_host_port
)
from lib.vault import Vault


def load_secrets(artsy_project, vault_host, vault_port, secrets_file, kvv2_mount_point):
  ''' load secrets from  Vault and write them to a file '''
  logging.info(f'Loading secrets from {vault_host}:{vault_port} under {kvv2_mount_point}')

  path = f'kubernetes/apps/{artsy_project}/'

  vault_client = Vault(
    url_host_port(vault_host, vault_port),
    auth_method='kubernetes',
#    auth_method='iam',
    role=artsy_project,
    kvv2_mount_point=kvv2_mount_point,
    path=path,
  )

  keys = vault_client.list()['data']['keys']

  logging.info(f'fetched keys from Vault: {keys}')

  with open(secrets_file, 'w') as f:
    for key in keys:
      try:
        value = vault_client.get(key)
        f.write(f'{key}={value}\n')
      except hvac.exceptions.InvalidPath:
        logging.info(f'{key} either does not exist or is soft deleted.')
