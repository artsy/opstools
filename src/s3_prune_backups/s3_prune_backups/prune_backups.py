import logging

import s3_prune_backups.context

from lib.artsy_s3_backup import ArtsyS3Backup

def prune(
  app,
  artsy_env,
  ndays,
  s3_bucket,
  s3_prefix,
  suffix,
  force
):
  ''' delete backups older than ndays '''
  logging.info(
    f"Deleting {app}'s {artsy_env} backups " +
    f"in S3 older than {ndays} days..."
  )
  artsy_s3_backup = ArtsyS3Backup(
    s3_bucket,
    s3_prefix,
    app,
    artsy_env,
    suffix
  )
  for backup_id in artsy_s3_backup.old_backups(ndays):
    if force:
      artsy_s3_backup.delete(backup_id)
      logging.info(f"Deleted {backup_id}")
    else:
      logging.info(f"Would have deleted {backup_id}")
  logging.info(
    f"Done deleting backups"
  )
