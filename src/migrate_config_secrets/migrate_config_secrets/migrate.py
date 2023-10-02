import logging

import migrate_config_secrets.context

from lib.k8s_configmap import ConfigMap
from lib.kctl import Kctl
from lib.vault import Vault

def migrate_config_secrets(artsy_env, artsy_project, secrets_list):
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

  for var in secrets:
    migrate_var(artsy_project, var, configmap_obj, artsy_env)

def identify_sensitive_vars(vars):
  ''' prompt user to say whether each var is sensitive '''
  sensitive = []
  for k,v in vars.items():
    answer = input(f"is {k}={v} sensitive (y/n)? ")
    if answer == 'y':
      sensitive += [k]
  return sensitive

def migrate_var(artsy_project, var, configmap_obj, artsy_env):
  ''' migrate one var from configmap to vault '''
  logging.info(f'Migrating {var} from k8s configmap to Vault...')
  value = configmap_obj.get(var)
  vault = Vault(artsy_project, artsy_env)
  vault.add(var, value)
