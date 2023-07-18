import datetime
import logging
import jwt

from distutils.dir_util import mkpath

import kubernetes_configmap_jwt_scan.context

from kubernetes_configmap_jwt_scan.config import config
from lib.jwt import is_jwt
from lib.kctl import Kctl

WARN_THRESHOLD = 30 # warn if expiring within 30 days

def scan():
  logging.info(f"Scanning {config.artsy_env}...")
  kctl = Kctl(config.in_cluster, config.artsy_env)
  results = {}
  now = datetime.datetime.now()
  for configmap in kctl.get_configmaps():
    if 'data' not in configmap:
      continue
    for key, val in configmap['data'].items():
      if is_jwt(val):
        logging.debug(f"Found {key} in {configmap['metadata']['name']} that looks like a JWT")
        payload = jwt.decode(val, options={"verify_signature": False, "verify_exp": False})
        if 'exp' in payload:
          exp_date = datetime.datetime.utcfromtimestamp(payload['exp'])
          days_to_expiry = (exp_date - now).days
          if days_to_expiry <= WARN_THRESHOLD:
            details = {
              'days_left': days_to_expiry,
              'aud': payload.get('aud'),
              'subject_application': payload.get('subject_application')
            }
            logging.error(f"Found expiring {key} in {configmap['metadata']['name']}: {details}")
            if configmap['metadata']['name'] not in results:
              results[configmap['metadata']['name']] = {}
            results[configmap['metadata']['name']][key] = details
  if results:
    raise SystemExit('Some tokens are expiring!')
  logging.info("Done")
