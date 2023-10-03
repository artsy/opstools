import logging
import os
import time

from hvac.exceptions import InvalidPath

import migrate_config_secrets.context

from lib.k8s_configmap import ConfigMap
from lib.k8s_secret import K8sSecret
from lib.kctl import Kctl
from lib.vault import Vault
from lib.util import run_cmd, vault_version

def migrate_config_secrets(artsy_env, artsy_project, secrets_list, repos_base_dir):
  ''' migrate all sensitive configs from configmap to vault '''
  logging.info(f'Migrating {artsy_env} {artsy_project} sensitive configs from k8s configmap to Vault...')
  # go through the list and create a list of secrets
  kctl = Kctl(False, artsy_env)
  configmap_name = f'{artsy_project}-environment'
  configmap_obj = ConfigMap(kctl, name=configmap_name)
  vars = configmap_obj.load()

  secrets = []
  if secrets_list is None:
    secrets = identify_sensitive_vars(vars)
  else:
    with open(secrets_list, 'r') as f:
      secrets = f.read().splitlines()

  vault_client = Vault(artsy_project, artsy_env)

  for var in secrets:
    migrate_var(vault_client, var, configmap_obj)

  # force sync vault -> eso
  epoch_time = int(time.time())
  kctl.annotate('externalsecret', artsy_project, f'force-sync={epoch_time}')

  # compare vault with k8s secret
  for var in secrets:
    compare_vault_k8s_secret(vault_client, kctl, var, artsy_project)

  project_repo_dir = os.path.join(repos_base_dir, artsy_project)
  logging.info('delete vars from configmap...')
  for var in secrets:
    logging.info(f'delete {var}...')
    run_cmd(f'hokusai {artsy_env} env unset {var}', project_repo_dir)

def compare_vault_k8s_secret(vault_client, kctl, var, artsy_project):
  logging.info(f'comparing Vault and k8s secret on {var} ...')
  vault_value = vault_client.get(var)
  k8s_secret_obj = K8sSecret(kctl, name=artsy_project)
  k8s_secret_value = k8s_secret_obj.get(var)
  if vault_value == vault_version(k8s_secret_value):
    logging.info(f'k8s secret and Vault match')
  else:
    logging.info(f"k8s secret and Vault don't match")
    raise

def identify_sensitive_vars(vars):
  ''' prompt user to say whether each var is sensitive '''
  sensitive = []
  for k,v in vars.items():
    answer = input(f"is {k}={v} sensitive (y/n)? ")
    if answer == 'y':
      sensitive += [k]
  return sensitive

def migrate_var(vault_client, var, configmap_obj):
  ''' migrate one var from configmap to vault '''
  logging.info(f'Migrating {var} ...')
  value = configmap_obj.get(var)
  # check if key exists and has value
  # don't want to just put, because it bumps version
  # even if value put is same as existing value
  try:
    value_in_vault = vault_client.get(var)
    # no exception means var exists and has value
    # see if value matches configmap
    if value_in_vault == vault_version(value):
      logging.info(f'{var} value in Vault matches configmap. nothing to do.')
    else:
      # values differ. update vault.
      logging.info(f'{var} value in Vault differs from configmap. making Vault match configmap... ')
      vault_client.set(var, value)
  except InvalidPath:
    logging.info(f'{var} does not exist or data soft-deleted.')
    # set it
    vault_client.set(var, value)
  except KeyError:
    # that means the k/v pair of vault entry has key that's not the same as var name
    # set it
    vault_client.set(var, value)
