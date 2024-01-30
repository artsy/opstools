import logging
import os
import tarfile

from distutils.dir_util import mkpath

import kubernetes_export.context

from lib.export_backup import (
  backup_to_s3,
  write_file
)
from lib.kctl import Kctl


def export(object_type, export_dir, kctl):
  ''' export object_type of k8s objects to a yaml file '''
  logging.info(f"Exporting {object_type}...")
  data = kctl.get_namespaced_object(object_type, 'yaml', 'default')
  output_file = os.path.join(export_dir, f"{object_type}.yaml")
  write_file(output_file, data, heading='---\n')

def export_and_backup(
  KUBERNETES_OBJECTS,
  artsy_env,
  in_cluster,
  local_dir,
  s3,
  s3_bucket,
  s3_prefix
):
  ''' export kubernetes objects to yaml files and optionally back them up to S3 '''
  export_dir = os.path.join(local_dir, artsy_env)
  mkpath(export_dir)
  logging.info(
    f"Exporting objects from {artsy_env} Kubernetes cluster," +
    f" default namespace, as yaml files, to {export_dir} ..."
  )
  kctl = Kctl(in_cluster, artsy_env)
  for object_type in KUBERNETES_OBJECTS:
    export(object_type, export_dir, kctl)
  logging.info("Done exporting")
  if s3:
    try:
      archive_file = os.path.join(
        local_dir, f"kubernetes-backup-{artsy_env}.tar.gz"
      )
      logging.info(f"Writing local archive file: {archive_file} ...")
      with tarfile.open(archive_file, "w:gz") as tar:
        tar.add(export_dir, arcname=os.path.basename(export_dir))
      backup_to_s3(
        s3_bucket,
        s3_prefix,
        'k8s',
        artsy_env,
        'tar.gz',
        archive_file,
        export_dir
      )
    except:
      raise
    finally:
      logging.info(f"Deleting {archive_file} ...")
      os.remove(archive_file)
  else:
    logging.info("Skipping backup to S3. Please delete the local files when done!")
