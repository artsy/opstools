import datetime
import logging
import jwt
import re


JWT_REGEX = re.compile(r'^(?:[\w-]*\.){2}[\w-]*$')

def is_jwt(str):
  if not JWT_REGEX.match(str):
    return False
  header = None
  try:
    header = jwt.get_unverified_header(str)
  except jwt.DecodeError as e:
    return False
  return header is not None

def jwt_expires_ndays(token, ndays):
  if not is_jwt(token):
    logging.debug('Token is not JWT')
    return False
  payload = jwt.decode(
    token,
    options={"verify_signature": False, "verify_exp": False}
  )
  if not 'exp' in payload:
    logging.debug('JWT has no exp field in payload')
    return False
  exp_date = datetime.datetime.utcfromtimestamp(payload['exp'])
  now = datetime.datetime.now()
  days_to_expiry = (exp_date - now).days
  logging.debug(f'JWT expires in {days_to_expiry} days')
  if days_to_expiry <= ndays:
    return True
