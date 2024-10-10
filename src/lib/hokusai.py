import logging

from lib.util import run_cmd


def env_unset(project_dir, env, var):
  ''' run hokusai env unset for var for project '''
  logging.debug(f'unsetting {var}...')
  run_cmd(f'hokusai {env} env unset {var}', project_dir)
