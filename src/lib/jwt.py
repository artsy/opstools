import re
import jwt

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
