import logging

import kubernetes_configmap_jwt_scan.context

from lib.jwt import jwt_expires_ndays
from lib.k8s_configmap import ConfigMaps
from lib.kctl import Kctl


def scan(artsy_env, ndays, in_cluster):
  logging.info(f"Scanning {artsy_env} configmaps for JWTs that will expire in < {ndays} days...")
  kctl = Kctl(in_cluster, artsy_env)
  configmaps = ConfigMaps(kctl)
  configmap_vars = configmaps.find_vars_by_value(jwt_expires_ndays, ndays)
  for configmap_name in list(configmap_vars.keys()):
    var_names = list(configmap_vars[configmap_name].keys())
    if var_names != []:
      logging.info(f'Found vars in {configmap_name} configmap: {var_names}')
