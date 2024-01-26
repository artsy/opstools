import logging
import os
import shutil

from distutils.dir_util import mkpath
from pathlib import Path

from lib.artsy_s3_backup import ArtsyS3Backup
from lib.validations import is_artsy_s3_bucket


def backup_to_s3(
  s3_bucket,
  s3_prefix,
  service_name,
  artsy_env,
  suffix,
  source_file,
  source_dir,
  cleanup=True
):
  ''' back up to S3 and if failure, cleanup '''
  if not is_artsy_s3_bucket(s3_bucket):
    raise Exception(f"{s3_bucket} seems not an Artsy S3 bucket.")
  try:
    artsy_s3_backup = ArtsyS3Backup(
      s3_bucket,
      s3_prefix,
      service_name,
      artsy_env,
      suffix
    )
    logging.info('Backing up to S3...')
    artsy_s3_backup.backup(source_file)
  except:
    raise
  finally:
    if cleanup:
      logging.info(f"Deleting {source_dir} ...")
      shutil.rmtree(source_dir)

def setup_local_export_dir(local_dir, artsy_env, service_host, suffix):
  '''
  set up a local dir to store data export,
  name dir after artsy environment,
  generate output file name,
  return dir and file name, expect client to create file.
  '''
  export_dir = os.path.join(local_dir, artsy_env)
  mkpath(export_dir)
  file_name = f"{service_host}.{suffix}"
  output_file = os.path.join(export_dir, file_name)
  return export_dir, output_file

def write_file(output_file, data, data_format='text', heading=None, mode=0o600, exist_ok=True):
  if data_format == 'text':
    write_text_file(output_file, data, heading, mode, exist_ok)
  elif data_format == 'binary':
    write_binary_file(output_file, data, mode, exist_ok)
  else:
    raise Exception(f'Un-supported data format: {data_format}')

def write_text_file(output_file, data, heading=None, mode=0o600, exist_ok=True):
  ''' write heading and data to output file, create file with proper permissions '''
  fobj = Path(output_file)
  fobj.touch(mode=mode, exist_ok=exist_ok)
  with open(output_file, 'w') as f:
    if heading:
      f.write(heading)
    f.write(data)

def write_binary_file(output_file, data, mode=0o600, exist_ok=True):
  ''' write data to output file, create file with proper permissions '''
  fobj = Path(output_file)
  fobj.touch(mode=mode, exist_ok=exist_ok)
  with open(output_file, 'wb') as f:
    f.write(data)
