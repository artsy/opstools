import os

import logging

import boto3

class S3Interface(object):
  KEY_SUFFIX = '.tar.gz'

  def __init__(self, bucket_name, prefix=''):
    self.client = boto3.client('s3')
    self.bucket_name = bucket_name
    self.bucket_prefix = prefix

  def _backup_name_to_s3_key(self, name):
    ''' given name of backup, return s3 key of backup '''
    key = os.path.join(self.bucket_prefix, name + self.KEY_SUFFIX)
    return key

  def _list_backups(self):
    ''' list content of s3 path that stores backups '''
    logging.debug(f"Listing s3://{self.bucket_name}/{self.bucket_prefix}")
    return sorted(
      map(lambda o: o['Key'],
      self.client.list_objects(
        Bucket=self.bucket_name,
        Prefix=self.bucket_prefix)['Contents']
      ),
      reverse=True
    )

  def _s3_key_to_backup_name(self, key):
    ''' given s3 key of backup, return name of backup '''
    object = key.replace("%s/" % self.bucket_prefix, '')
    name = object.replace(self.KEY_SUFFIX, '')
    return name

  def backups(self):
    ''' return a list of backups, ordered from most recent to oldest '''
    backups = []
    for k in self._list_backups():
      if self.KEY_SUFFIX not in k:
        continue
      backups.append(self._s3_key_to_backup_name(k))
    logging.debug("Found backups:")
    logging.debug(backups)
    return backups

  def put_file(self, file_path, key):
    with open(file_path, 'rb') as f:
      self.client.upload_fileobj(f, self.bucket_name, key)

  def backup(self, file_path, backup_name):
    self.put_file(
      file_path,
      self._backup_name_to_s3_key(backup_name)
    )
    return os.path.join(self.bucket_prefix, backup_name)

  def delete(self, backup_name):
    self.client.delete_object(
      Bucket=self.bucket_name,
      Key=self._backup_name_to_s3_key(backup_name)
    )
    return os.path.join(self.bucket_prefix, backup_name)
