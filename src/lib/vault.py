import logging
import os

from subprocess import run as subprocess_run


class Vault:
  ''' interface with hashicorp vault client '''
  def __init__(self, artsy_project, artsy_env):
    prefix = 'kvv2/kubernetes/apps/'
    self._path = f'{prefix}{artsy_project}/'

    self.artsy_env = artsy_env

    env_var_name = f'{artsy_env.upper()}_VAULT_ADDR'
    self.vault_addr = os.environ.get(env_var_name)

    assume_role_var_name = f'{artsy_env.upper()}_VAULT_ASSUME_ROLE_STRING'
    self.assume_role_string = os.environ.get(assume_role_var_name)

    self.role_name = os.environ.get('VAULT_ROLE_NAME')

  def _run(self, command, timeout=30, expect_success=False):
    ''' run command using vault and return result '''
    login_cmd = (
      f'export VAULT_ADDR={self.vault_addr};' +
      f'creds=`{self.assume_role_string}`;' +
      f'export AWS_ACCESS_KEY_ID=`jq -r .AccessKeyId <<< $creds`;' +
      f'export AWS_SECRET_ACCESS_KEY=`jq -r .SecretAccessKey <<< $creds`;' +
      f'export AWS_SESSION_TOKEN=`jq -r .SessionToken <<< $creds`;' +
      f'vault login -method=aws role={self.role_name};'
    )
    vault_cmd = f"vault {command}"
    cmd = login_cmd + vault_cmd
    logging.debug(f"Vault: running {cmd}")
    # exception not raised if run fails
    resp = subprocess_run(
      cmd,
      capture_output=True,
      shell=True,
      text=True,
      timeout=timeout
    )
    if expect_success and resp.returncode != 0:
      raise Exception(
        f"Command failed: {command}\n" +
        f"Stderr from Command: {resp.stderr}"
      )
    return resp

  def add(self, key, value):
    ''' add a kv entry '''
    full_path = f'{self._path}{key}'
    cleaned_value = self.clean_value(value)
    cmd = f"kv put -cas=0 {full_path} {key}='{cleaned_value}'"
    logging.debug(cmd)
    self._run(cmd, expect_success=True)

  def clean_value(self, value_string):
    '''
    double quote strings that contain special YAML characters,
    such as asterisk,
    otherwise ESO won't be able to parse
    '''
    special_chars = ['*']
    for char in special_chars:
      if char in value_string:
        return f'"{value_string}"'
    return value_string
