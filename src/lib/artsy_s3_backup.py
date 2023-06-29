import logging
import os

from datetime import datetime

from lib.s3_interface import S3Interface

class ArtsyS3Backup:
  def __init__(self, s3_bucket, s3_prefix, artsy_app, artsy_env, filename_suffix):
    self.s3_bucket = s3_bucket
    self._full_prefix = os.path.join(s3_prefix, artsy_app, artsy_env)
    self._s3_interface = S3Interface()
    self._key_suffix = filename_suffix

  def backup(self, source_path):
    backup_id = str(datetime.utcnow()).replace(' ', '_')
    key = f"{self._full_prefix}/{backup_id}.{self._key_suffix}"
    logging.info(
      f"Copying {source_path} to s3://{self.s3_bucket}/{key} ..."
    )
    self._s3_interface.put_file(source_path, self.s3_bucket, key)
