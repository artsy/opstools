import migrate_config_secrets.context

from lib.kctl import Kctl
from lib.k8s_configmap import ConfigMap

def migrate_config_secrets(artsy_env, artsy_project, secrets_list):
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

def identify_sensitive_vars(vars):
  sensitive = []
  for k,v in vars.items():
    answer = input(f"is {k}={v} sensitive (y/n)? ")
    if answer == 'y':
      sensitive += [k]
  return sensitive
