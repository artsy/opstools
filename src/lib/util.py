import glob
import logging
import os
import subprocess

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

def is_artsy_s3_bucket(name):
  ''' return true if bucket name starts with artsy- '''
  return name.startswith('artsy-')

def is_quoted(str1):
  ''' if string is quoted, return the quote character '''
  # double quote
  if str1[0] == '"' and str1[-1] == '"':
    return '"'
  # single quote
  elif str1[0] == "'" and str1[-1] == "'":
    return "'"

def list_intersect(list_a, list_b):
  ''' return elements common between l1 and l2 '''
  return [ x for x in list_a if x in list_b]

def list_match_str(list_a, str1):
  ''' return elements of list_a that match string str1 '''
  return [x for x in list_a if str1 in x]

def list_subtract(list_a, *args):
  '''
  return elements that are in list a but
  not in any list supplied by *args
  '''
  minuend = list_a
  for subtrahend in args:
    minuend = [x for x in minuend if x not in subtrahend]
  return minuend

def match_or_raise(str1, str2):
  ''' raise if str1 and str2 differ '''
  if str1 == str2:
    logging.debug('str1 and str2 match')
  else:
    logging.error('str1 and str2 different')
    raise

def parse_string_of_key_value_pairs(str1):
  '''
  given 'foo:x,foo:y,bar:x',
  return {'foo': ['x', 'y'], 'bar': ['x']}
  '''
  dict1 = {}
  for kv in str1.split(','):
    k, v = kv.split(':')
    dict1[k] = dict1.get(k, []) + [v]
  return dict1

def run_cmd(cmd, dirx, timeout=300):
  ''' run command in dir and return output '''
  os.chdir(dirx)
  logging.info(f"running {cmd} command in {dirx} directory.")
  resp = subprocess.run(
    cmd,
    capture_output=True,
    shell=True,
    text=True,
    timeout=timeout
  )
  logging.info(
    f"{cmd} command exited with code {resp.returncode}"
  )
  # this might print sensitive info so please use only locally
  logging.debug(
    f"{cmd} stdout:\n{resp.stdout}"
    f"{cmd} stderr:\n{resp.stderr}"
  )
  return resp

def search_dirs_by_suffix(dirx, suffix):
  ''' return dirx's subdirs that contain files with the given suffix '''
  globstr = f"{dirx}/**/*.{suffix}"
  files = [
    path for path in glob.glob(globstr, recursive=True)
    if os.path.isfile(path)
  ]
  dirs = [os.path.dirname(path) for path in files]
  return sorted(list(set(dirs)))

def unquote(str1):
  ''' remove string's surrounding quotes, if any '''
  quote_char = is_quoted(str1)
  if quote_char:
    logging.debug(f'string is quoted with {quote_char}, removing quotes')
    return str1[1:-1]
  return str1
