def is_artsy_s3_bucket(name):
  ''' return true if bucket name starts with artsy- '''
  return name.startswith('artsy-')

def is_artsy_staging_internal_hostname(name):
  ''' return true if name ends with stg.artsy.systems'''
  return name.endswith('stg.artsy.systems')

def is_artsy_production_internal_hostname(name):
  ''' return true if name ends with prd.artsy.systems'''
  return name.endswith('prd.artsy.systems')

def hostname_agrees_with_artsy_environment(name, artsy_env):
  '''
  return true if environment is staging and
  name is artsy staging internal hostname,
  similarly for production
  '''
  if artsy_env == 'staging':
    return is_artsy_staging_internal_hostname(name)
  elif artsy_env == 'production':
    return is_artsy_production_internal_hostname(name)
  else:
    raise Exception(f'Unknown Artsy environment: {artsy_env}')
