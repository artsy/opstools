import vault_snapshot.context

from lib.vault import Vault


def take_snapshot(
  local_dir,
  artsy_env,
  vault_addr,
  s3,
  s3_bucket,
  s3_prefix
):
  vault_client = Vault(vault_addr, 'iam', role='opstools-role')
