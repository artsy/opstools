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

  def _backup_name_to_s3_key(self, name):
    ''' given name of backup, return s3 key of backup '''
    key = os.path.join(self._full_prefix, f"{name}.{self._key_suffix}")
    return key

  def _s3_key_to_backup_name(self, key):
    ''' given s3 key of backup, return name of backup '''
    object = key.replace(f"{self._full_prefix}/", '')
    name = object.replace(f".{self._key_suffix}", '')
    return name

  def backup(self, source_path):
    ''' backup a file to S3 '''
    backup_id = str(datetime.utcnow()).replace(' ', '_')
    key = f"{self._full_prefix}/{backup_id}.{self._key_suffix}"
    logging.info(
      f"Copying {source_path} to s3://{self.s3_bucket}/{key} ..."
    )
    self._s3_interface.put_file(source_path, self.s3_bucket, key)

  def delete(self, name):
    ''' delete the backup identified by name '''
    self._s3_interface.delete_object(
      self.s3_bucket,
      self._backup_name_to_s3_key(name)
    )

  def backups(self):
    ''' return a list of backups, ordered from most recent to oldest '''
    logging.info(
      f"ArtsyS3Backup: listing backups in s3://{self.s3_bucket}/{self._full_prefix}/"
    )
    data = self._s3_interface.list_objects(self.s3_bucket, self._full_prefix)
    files = sorted(
      map(lambda o: o['Key'], data['Contents']),
      reverse=True
    )
    backups = []
    for k in files:
      if self._key_suffix not in k:
        continue
      backups.append(self._s3_key_to_backup_name(k))
    logging.debug("Found backups:")
    logging.debug(backups)
    return backups
