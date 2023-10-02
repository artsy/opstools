import migrate_config_secrets.context

from lib.hokusai import Hokusai

def migrate_config_secrets(artsy_env, git_repos_base_dir, artsy_project):
  # go through the list and create a list of secrets
  hokusai = Hokusai(artsy_env, git_repos_base_dir, artsy_project)
  env_vars = hokusai.env_get()
  print(env_vars.keys())
