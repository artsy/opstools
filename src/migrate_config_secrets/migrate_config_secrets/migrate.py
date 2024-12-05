import logging
import os

import datetime
import jwt
import time

import migrate_config_secrets.context

from lib.hokusai import env_unset
from lib.jwt import is_jwt
from lib.k8s_configmap import ConfigMap
from lib.kctl import Kctl
from lib.util import (
  match_or_raise,
  url_host_port
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

def compare_vault_configmap(vault_client, configmap_obj, var):
  ''' raise if Vault and Configmap values for var different '''
  configmap_value = configmap_obj.get(var)
  vault_value = vault_client.get(var)
  match_or_raise(vault_value, configmap_value)

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
  in_cluster = False
  kctl = Kctl(in_cluster, artsy_env)
  configmap_name = f'{artsy_project}-environment'
  configmap_obj = ConfigMap(kctl, configmap_name)
  vault_path = 'kubernetes/apps/' + f'{artsy_project}/'

  logging.info(
    f'Migrating sensitive configs from {artsy_env} {configmap_name} configmap to {vault_path} in Vault...'
  )

  vault_client = Vault(
    url_host_port(vault_host, vault_port),
    auth_method='iam',
    kvv2_mount_point=kvv2_mount_point,
    path=vault_path,
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

  if not dry_run:
    logging.info('Moving vars from ConfigMap to Vault...')
    move_vars(vault_client, configmap_obj, sensitive_vars, repos_base_dir, artsy_project, artsy_env)

def move_vars(vault_client, configmap_obj, var_names, repos_base_dir, artsy_project, artsy_env):
  ''' configure vars in Vault '''
  project_repo_dir = os.path.join(repos_base_dir, artsy_project)

  for var in var_names:
    logging.info(f'Moving {var} from ConfigMap to Vault...')
    configmap_value = configmap_obj.get(var)
    vault_client.get_set(var, configmap_value)
    logging.info('Checking if Vault and configmap have same value...')
    compare_vault_configmap(vault_client, configmap_obj, var)

    # set expire_at meta if jwt
    if is_jwt(configmap_value):
      logging.info(f"Value is a JWT.")
      set_exp_meta(vault_client, var, configmap_value)

    # ask user about deleting var in configmap
    answer = input(f'would you like to delete {var} from configmap (y/n)? ')
    if answer == 'y':
      logging.info(f'Deleting {var} from configmap...')
      env_unset(project_repo_dir, artsy_env, var)

def set_exp_meta(vault_client, var, jwt_str):
  ''' extract expiration date from jwt payload and set it in vault custom metadata '''
  exp_date_filler = 'nil'
  exp_date_meta_key = 'expires_at'
  payload = jwt.decode(jwt_str, options={"verify_signature": False, "verify_exp": False})
  if 'exp' in payload and payload['exp'] is not None:
    exp_payload = payload['exp']
    logging.info(f"JWT has exp payload: {exp_payload}")
    exp_date = datetime.datetime.utcfromtimestamp(exp_payload)
    logging.info(f"Exp payload to date: {exp_date}")
    exp_date_str = exp_date.isoformat("T") + "Z"
  else:
    logging.info(f"JWT does not have exp payload or exp payload is not valid")
    exp_date_str = exp_date_filler
  logging.info(f"Setting custom expire_at metadata: {exp_date_str}")
  vault_client.update_custom_meta(var, exp_date_meta_key, exp_date_str)
