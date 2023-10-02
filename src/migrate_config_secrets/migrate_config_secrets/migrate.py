import migrate_config_secrets.context

from lib.kctl import Kctl
from lib.k8s_configmap import ConfigMap

def migrate_config_secrets(artsy_env, artsy_project):
  # go through the list and create a list of secrets
  kctl = Kctl(False, artsy_env)
  configmap_name = f'{artsy_project}-environment'
  configmap_obj = ConfigMap(kctl, name=configmap_name)
  print(configmap_obj.load().keys())
