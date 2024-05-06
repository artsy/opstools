import logging
import os
import time

import migrate_config_secrets.context

from lib.hokusai import env_unset
from lib.k8s_configmap import ConfigMap
from lib.k8s_secret import K8sSecret
from lib.kctl import Kctl
from lib.util import (
  match_or_raise,
  url_host_port
)
from lib.sanitizers import (
  config_secret_sanitizer,
  config_secret_sanitizer_artsy
)
from lib.vault import Vault


def ask_user_to_identify_sensitive_vars(keys_values):
  ''' var by var, ask user whether it is sensitive '''
  sensitive = []
  for k,v in keys_values.items():
    answer = input(f"is {k}={v} sensitive (y/n)? ")
    if answer == 'y':
      sensitive += [k]
  return sensitive

def compare_k8s_secret_configmap(secret_obj, configmap_obj, sensitive_vars):
  ''' compare k8s secret and configmap, var by var '''
  for var in sensitive_vars:
    logging.debug(f'Comparing {var} ...')
    k8s_secret_value = secret_obj.get(var)
    configmap_value = configmap_obj.get(var)
    match_or_raise(
      k8s_secret_value,
      config_secret_sanitizer_artsy(configmap_value)
    )

def get_sensitive_vars(configmap_obj, artsy_project, artsy_env):
  configmap_vars = configmap_obj.load()
  sensitive_vars = ask_user_to_identify_sensitive_vars(
    configmap_vars
  )
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
  vault_host,
  vault_port,
  kvv2_mount_point,
  dry_run
):
  ''' migrate sensitive configs from configmap to Vault '''
  kctl = Kctl(False, artsy_env)
  configmap_name = f'{artsy_project}-environment'
  configmap_obj = ConfigMap(kctl, configmap_name)

  secret_obj = K8sSecret(kctl, artsy_project)
  path = 'kubernetes/apps/' + f'{artsy_project}/'

  logging.info(
    f'Migrating sensitive configs from {artsy_env} {configmap_name} configmap to {path} in Vault...'
  )

  vault_client = Vault(
    url_host_port(vault_host, vault_port),
    auth_method='iam',
    kvv2_mount_point=kvv2_mount_point,
    path=path,
    sanitizer=config_secret_sanitizer
  )

  logging.info('Getting list of sensitive vars...')
  if list is not None:
    # a list of sensitive vars is provided
    with open(list, 'r') as f:
      sensitive_vars = f.read().splitlines()
  else:
    # no list
    sensitive_vars = get_sensitive_vars(
      configmap_obj, artsy_project, artsy_env
    )

  logging.info('Configuring vars in Vault...')
  update_vault(vault_client, configmap_obj, sensitive_vars, dry_run)

  if dry_run:
    logging.info('Skipping the rest because this is a dry run.')
  else:
    logging.info('Syncing vars from Vault to k8s secret...')
    sync_vault_k8s_secret(
      kctl, vault_client, secret_obj, artsy_project, sensitive_vars
    )

    logging.info('Comparing k8s secret with configmap...')
    compare_k8s_secret_configmap(secret_obj, configmap_obj, sensitive_vars)

    logging.info('Deleting vars from configmap...')
    project_repo_dir = os.path.join(repos_base_dir, artsy_project)
    env_unset(project_repo_dir, artsy_env, sensitive_vars)

def sync_vault_k8s_secret(
  kctl,
  vault_client,
  secret_obj,
  artsy_project,
  sensitive_vars
):
  logging.info('Force sync Vault -> k8s secret...')
  epoch_time = int(time.time())
  kctl.annotate(
    'externalsecret', artsy_project, f'force-sync={epoch_time}'
  )
  # allow annotate to finish
  time.sleep(10)

  # confirm the two are in sync, var by var
  logging.info(
    'Comparing values in Vault with values in k8s secret...'
  )
  for var in sensitive_vars:
    logging.debug(f'Comparing {var} ...')
    vault_value = vault_client.get(var)
    k8s_secret_value = secret_obj.get(var)
    match_or_raise(
      vault_value,
      config_secret_sanitizer(k8s_secret_value)
    )

def update_vault(vault_client, configmap_obj, var_names, dry_run):
  ''' configure vars in Vault '''
  for var in var_names:
    logging.debug(f'Updating {var} value in Vault...')
    configmap_value = configmap_obj.get(var)
    vault_client.get_set(var, configmap_value, dry_run)
