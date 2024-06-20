import logging
import os
import time

import migrate_config_secrets.context

from lib.hokusai import env_unset
from lib.k8s_configmap import ConfigMap
from lib.k8s_secret import K8sSecret
from lib.kctl import Kctl
from lib.util import (
  list_to_multiline_string,
  match_or_raise,
  url_host_port
)
from lib.sanitizers import (
  config_secret_sanitizer,
  config_secret_sanitizer_artsy
)
from lib.vault import Vault


def compare_k8s_secret_configmap(var_name, secret_obj, configmap_obj):
  ''' compare k8s secret and configmap for specified var '''
  logging.info(f'Comparing var {var_name} between K8S Secret and ConfigMap ...')
  k8s_secret_value = secret_obj.get(var_name)
  configmap_value = configmap_obj.get(var_name)
  match_or_raise(
    k8s_secret_value,
    config_secret_sanitizer_artsy(configmap_value)
  )

def compare_vault_k8s_secret(vault_client, secret_obj, var_name):
  logging.info(
    f'Comparing var {var_name} between Vault and K8S Secret...'
  )
  vault_value = vault_client.get(var_name)
  k8s_secret_value = secret_obj.get(var_name)
  match_or_raise(
    vault_value,
    config_secret_sanitizer(k8s_secret_value)
  )

def migrate_config_secrets(
  artsy_env,
  artsy_project,
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

  vault_client = Vault(
    url_host_port(vault_host, vault_port),
    auth_method='iam',
    kvv2_mount_point=kvv2_mount_point,
    path=path,
    sanitizer=config_secret_sanitizer
  )

  configmap_vars = configmap_obj.load()

  logging.info(
    f'Migrating sensitive configs from {artsy_env} {configmap_name} configmap to {path} in Vault...'
  )

  sensitive = []
  for var_name, var_value in configmap_vars.items():
    answer = None
    while answer != 'y' and answer != 'n':
      answer = input(f"is {var_name}={var_value} sensitive (y/n)? ")
    if answer == 'y':
      sensitive += [var_name]
      if dry_run:
        logging.info('Skipping the rest because this is a dry run.')
      else:
        update_vault(
          var_name,
          kctl,
          vault_client,
          configmap_obj,
          secret_obj,
          artsy_project,
        )
        compare_k8s_secret_configmap(var_name, secret_obj, configmap_obj)

        logging.info(f'Deleting var {var_name} from configmap...')
        project_repo_dir = os.path.join(repos_base_dir, artsy_project)
        env_unset(var_name, project_repo_dir, artsy_env)

  logging.info(
    f'Identified {len(sensitive)} sensitive vars:\n' +
    f'{list_to_multiline_string(sensitive)}'
  )

def sync_vault_k8s_es(
  kctl,
  vault_client,
  secret_obj,
  artsy_project
):
  logging.info('Force sync Vault -> k8s ExternalSecret...')
  epoch_time = int(time.time())
  kctl.annotate(
    'externalsecret', artsy_project, f'force-sync={epoch_time}'
  )
  # allow annotate to finish
  time.sleep(10)

def update_vault(
  var_name,
  kctl,
  vault_client,
  configmap_obj,
  secret_obj,
  artsy_project,
):
  ''' configure a var in Vault '''
  logging.info(f'Configuring var {var_name} in Vault...')
  configmap_value = configmap_obj.get(var_name)
  vault_client.get_set(var_name, configmap_value)
  sync_vault_k8s_es(
    kctl, vault_client, secret_obj, artsy_project
  )
  compare_vault_k8s_secret(vault_client, secret_obj, var_name)
