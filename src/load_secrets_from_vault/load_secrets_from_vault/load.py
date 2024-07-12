import logging
import os

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
    auth_method='iam',
    kvv2_mount_point=kvv2_mount_point,
    path=path,
  )

  vault_value = vault_client.get('BAR')

  logging.info(f'fetched value from Vault for BAR: {vault_value}')

  with open(secrets_file, 'w') as f:
    f.write(f'DATA={vault_value}')
