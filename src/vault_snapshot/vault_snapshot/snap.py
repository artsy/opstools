import logging
import os
from distutils.dir_util import mkpath

import vault_snapshot.context

from lib.util import (
  backup_to_s3,
  url_host_port
)
from lib.vault import Vault


def take_snapshot(
  local_dir,
  artsy_env,
  vault_host,
  vault_port,
  vault_role,
  s3,
  s3_bucket,
  s3_prefix
):
  vault_client = Vault(
    url_host_port(vault_host, vault_port),
    'iam',
    role=vault_role
  )
  export_dir = os.path.join(local_dir, artsy_env)
  mkpath(export_dir)
  file_name = f"{vault_host}.gz"
  output_file = os.path.join(export_dir, file_name)
  logging.info('Taking snapshot...')
  vault_client.take_snapshot(output_file)
  if s3:
    backup_to_s3(
      s3_bucket,
      s3_prefix,
      'vault',
      artsy_env,
      'gz',
      output_file,
      export_dir
    )
  else:
    logging.info(
      "Skipping backup to S3. Please delete the local files when done!"
    )
