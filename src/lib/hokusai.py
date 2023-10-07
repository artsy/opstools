import logging

from lib.util import run_cmd


def env_unset(project_dir, env, var_names):
  ''' run hokusai env unset for vars for project '''
  for var in var_names:
    logging.debug(f'unsetting {var}...')
    run_cmd(f'hokusai {env} env unset {var}', project_dir)
