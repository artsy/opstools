import logging
import os
import time

import migrate_config_secrets.context

from lib.hokusai import env_unset
from lib.k8s_configmap import ConfigMap
from lib.k8s_secret import K8sSecret
from lib.kctl import Kctl
from lib.util import vault_string
from lib.vault import Vault


def ask_user_to_identify_sensitive_vars(keys_values):
  ''' var by var, ask user whether it is sensitive '''
  sensitive = []
  for k,v in keys_values.items():
    answer = input(f"is {k}={v} sensitive (y/n)? ")
    if answer == 'y':
      sensitive += [k]
  return sensitive

def get_sensitive_vars(configmap_obj, artsy_project, artsy_env):
  configmap_vars = configmap_obj.load()
  sensitive_vars = ask_user_to_identify_sensitive_vars(configmap_vars)
  file_path = f'./{artsy_project}_{artsy_env}_secret_vars.txt'
  logging.info(f'Saving list of sensitive vars in {file_path}')
  with open(file_path, 'w') as f:
    for var in sensitive_vars:
      f.write(f'{var}\n') 
  return sensitive_vars

def migrate_config_secrets(
  artsy_env,
  artsy_project,
  list,
  repos_base_dir,
  vault_addr,
  kvv2_mount_point,
  vault_token
):
  ''' migrate sensitive configs from configmap to Vault '''
  logging.info(f'Migrating {artsy_env} {artsy_project} sensitive configs from k8s configmap to Vault...')

  kctl = Kctl(False, artsy_env)
  configmap_name = f'{artsy_project}-environment'
  configmap_obj = ConfigMap(kctl, name=configmap_name)

  secret_obj = K8sSecret(kctl, name=artsy_project)

  path = 'kubernetes/apps/' + f'{artsy_project}/'
  vault_client = Vault(vault_addr, kvv2_mount_point, path, vault_token)

  logging.info('Getting list of sensitive vars...')
  if list is not None:
    # a list of sensitive vars is provided
    with open(list, 'r') as f:
      sensitive_vars = f.read().splitlines()
  else:
    # no list
    sensitive_vars = get_sensitive_vars(configmap_obj, artsy_project, artsy_env)

  logging.info('Configuring vars in Vault...')
  update_vault(vault_client, configmap_obj, sensitive_vars)

  logging.info('Syncing vars from Vault to k8s secret...')
  sync_vault_k8s_secret(kctl, vault_client, secret_obj, artsy_project, sensitive_vars)

  logging.info('Deleting vars from configmap...')
  project_repo_dir = os.path.join(repos_base_dir, artsy_project)
  env_unset(project_repo_dir, artsy_env, sensitive_vars)

def sync_vault_k8s_secret(kctl, vault_client, secret_obj, artsy_project, sensitive_vars):
  logging.info('Force sync Vault -> k8s secret...')
  epoch_time = int(time.time())
  kctl.annotate('externalsecret', artsy_project, f'force-sync={epoch_time}')
  # allow annotate to finish
  time.sleep(10)

  # confirm the two are in sync, var by var
  logging.info('Comparing values in Vault with values in k8s secret...')
  for var in sensitive_vars:
    logging.debug(f'Comparing {var} ...')
    vault_value = vault_client.get(var)
    k8s_secret_value = secret_obj.get(var)
    if vault_value == vault_string(k8s_secret_value):
      logging.debug(f'{var} match')
    else:
      logging.error(f"{var} doesn't match")
      raise

def update_vault(vault_client, configmap_obj, var_names):
  ''' configure vars in Vault '''
  for var in var_names:
    logging.debug(f'Updating {var} value in Vault...')
    configmap_value = configmap_obj.get(var)
    vault_client.get_set(var, configmap_value)
