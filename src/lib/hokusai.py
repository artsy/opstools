import logging

from lib.util import run_cmd


def env_unset(var_name, project_dir, env):
  ''' run hokusai env unset for specified var '''
  logging.debug(f'unsetting {var_name}...')
  run_cmd(f'hokusai {env} env unset {var_name}', project_dir)
