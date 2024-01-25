import logging
import os
import shutil

from distutils.dir_util import mkpath

import vault_snapshot.context

from lib.artsy_s3_backup import ArtsyS3Backup
from lib.vault import Vault


def take_snapshot(
  local_dir,
  artsy_env,
  vault_host,
  vault_port,
  s3,
  s3_bucket,
  s3_prefix
):
  vault_client = Vault(
    f'https://{vault_host}:{vault_port}',
    'iam',
    role='opstools-role'
  )
  export_dir = os.path.join(local_dir, artsy_env)
  mkpath(export_dir)
  file_name = f"{vault_host}.gz"
  output_file = os.path.join(export_dir, file_name)
  logging.info('Taking snapshot...')
  vault_client.take_snapshot(output_file)
  if s3:
    try:
      artsy_s3_backup = ArtsyS3Backup(
        s3_bucket,
        s3_prefix,
        'vault',
        artsy_env,
        'gz'
      )
      logging.info('Backing up to S3...')
      artsy_s3_backup.backup(output_file)
    except:
      raise
    finally:
      logging.info(f"Deleting {export_dir} ...")
      shutil.rmtree(export_dir)
  else:
    logging.info(
      "Skipping backup to S3. Please delete the local files when done!"
    )
