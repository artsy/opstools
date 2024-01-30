import logging

from lib.util import unquote


def config_secret_sanitizer(str1):
  ''' run all config secret sanitizers '''
  artsy_sanitized = config_secret_sanitizer_artsy(str1)
  eso_sanitized = config_secret_sanitizer_eso(artsy_sanitized)
  return eso_sanitized

def config_secret_sanitizer_artsy(str1):
  ''' ensure secret_value conforms to Artsy requirements '''
  # strip surrounding quotes if any
  return unquote(str1)

def config_secret_sanitizer_eso(str1):
  ''' ensure string is acceptable to Kubernetes External Secrets Operator '''
  # add double quoutes if string has YAML special char
  special_chars = ['*']
  for char in special_chars:
    if char in str1:
      logging.debug(
        'String contains special YAML chars, adding double-quotes.'
      )
      return f'"{str1}"'
      break
  return str1
