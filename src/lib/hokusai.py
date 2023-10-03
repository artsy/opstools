import logging

from lib.util import run_cmd


def env_unset(project_dir, env, vars):
  ''' run hokusai env unset for vars for project '''
  for var in vars:
    logging.debug(f'unsetting {var}...')
    run_cmd(f'hokusai {env} env unset {var}', project_dir)
