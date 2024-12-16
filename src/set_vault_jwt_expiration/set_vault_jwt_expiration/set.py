import logging

import datetime
import jwt

import set_vault_jwt_expiration.context

from lib.jwt import is_jwt
from lib.util import (
  url_host_port
)
from lib.vault import Vault


def set_jwt_expiration(
  artsy_env,
  artsy_project,
  vault_host,
  vault_port,
  kvv2_mount_point,
):
  ''' set expires_at custom header for all JWTs '''
  vault_path = 'kubernetes/apps/' + f'{artsy_project}/'
  vault_client = Vault(
    url_host_port(vault_host, vault_port),
    auth_method='iam',
    kvv2_mount_point=kvv2_mount_point,
    path=vault_path,
  )
  # get list of jwt vars
  jwt_vars = vault_client.list(match_function=is_jwt, match_type='value')
  logging.info(f'List of JWTs: {jwt_vars}')
  for var in jwt_vars:
    logging.info(
      f"Checking JWT {var}..."
    )
    jwt_string = vault_client.get(var)
    set_exp_meta(vault_client, var, jwt_string)

def set_exp_meta(vault_client, var, jwt_str):
  ''' extract expiration date from jwt payload and set it in vault custom metadata '''
  exp_date_filler = 'nil'
  exp_date_meta_key = 'expires_at'
  payload = jwt.decode(
    jwt_str,
    options={"verify_signature": False, "verify_exp": False}
  )
  if 'exp' in payload and payload['exp'] is not None:
    exp_payload = payload['exp']
    logging.info(f"JWT has exp payload: {exp_payload}")
    exp_date = datetime.datetime.utcfromtimestamp(exp_payload)
    logging.info(f"Exp payload to date: {exp_date}")
    exp_date_str = exp_date.isoformat("T") + "Z"
  else:
    logging.info(
      f"JWT does not have exp payload or exp payload is not valid"
    )
    exp_date_str = exp_date_filler
  answer = input(
    f'would you like to set custom metadata expires_at for {var} to {exp_date_str}: (y/n)? '
  )
  if answer == 'y':
    logging.info(f'Setting...')
    vault_client.update_custom_meta(var, exp_date_meta_key, exp_date_str)
