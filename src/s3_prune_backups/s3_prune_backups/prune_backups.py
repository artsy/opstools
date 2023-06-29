import logging
import os

from lib.artsy_s3_backup import ArtsyS3Backup

from s3_prune_backups.config import config

def prune():
  ''' delete backups older than ndays '''
  logging.info(
    f"Deleting {config.app}'s {config.artsy_env} backups in S3 older than {config.ndays} days..."
  )
  artsy_s3_backup = ArtsyS3Backup(config.s3_bucket, config.s3_prefix, config.app, config.artsy_env, config.suffix)
  for backup_id in artsy_s3_backup.backups()[config.ndays:]:
    if config.force:
      artsy_s3_backup.delete(backup_id)
      logging.info(f"Deleted {backup_id}")
    else:
      logging.info(f"Would have deleted {backup_id}")
  logging.info(
    f"Done deleting backups"
  )
