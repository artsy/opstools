import os
import shutil
import sys

import logging
import tarfile

from datetime import datetime
from distutils.dir_util import mkpath
from subprocess import check_output, CalledProcessError

from kubernetes_backup.config import config
from lib.artsy_s3_backup import ArtsyS3Backup

from lib.kctl import Kctl

def backup_to_s3(export_dir):
  ''' back up yamls to S3 '''
  archive_file = os.path.join(
                   config.local_dir, f"kubernetes-backup-{config.artsy_env}.tar.gz"
                 )
  logging.info(f"Writing local archive file: {archive_file} ...")
  with tarfile.open(archive_file, "w:gz") as tar:
    tar.add(export_dir, arcname=os.path.basename(export_dir))
  try:
    artsy_s3_backup = ArtsyS3Backup(config.s3_bucket, config.s3_prefix, 'k8s', config.artsy_env, 'tar.gz')
    artsy_s3_backup.backup(archive_file)
  except:
    raise
  finally:
    logging.info(f"Deleting {archive_file} ...")
    os.remove(archive_file)

def export(object_type, export_dir):
  ''' export object_type of k8s objects into a yaml file '''
  logging.info(f"Exporting {object_type}...")
  kctl = Kctl(config.in_cluster, config.artsy_env)
  data = kctl.get_default_namespace_objects(object_type, 'yaml')
  with open(os.path.join(export_dir, f"{object_type}.yaml"), 'w') as f:
    f.write('---\n')
    f.write(data.decode("utf-8"))

def export_and_backup(KUBERNETES_OBJECTS):
  ''' export kubernetes objects to yaml files and optionally back them up to S3 '''
  export_dir = os.path.join(config.local_dir, config.artsy_env)
  mkpath(export_dir)

  logging.info(
    f"Exporting objects from Kubernetes {config.artsy_env} cluster, default namespace, as yaml files, to {export_dir} ..."
  )
  for object_type in KUBERNETES_OBJECTS:
    try:
      export(object_type, export_dir)
    except CalledProcessError as e:
      logging.critical(f"Failed to export {object_type} to yaml: {e} Aborting.")
      shutil.rmtree(export_dir)
      sys.exit(1)
  logging.info("Done exporting")

  if config.s3:
    try:
      backup_to_s3(export_dir)
    except:
      raise
    finally:
      logging.info(f"Deleting {export_dir} ...")
      shutil.rmtree(export_dir)
  else:
    logging.info("Skipping backup to S3. Please delete the local files when done!")
