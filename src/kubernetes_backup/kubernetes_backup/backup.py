import os
import shutil
import sys

import logging
import tarfile

from datetime import datetime
from distutils.dir_util import mkpath
from subprocess import check_output, CalledProcessError

from kubernetes_backup.config import config
from kubernetes_backup.s3 import S3Interface
from lib.artsy_s3_backup import ArtsyS3Backup

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

def export(obj, export_dir):
  ''' export k8s object into a yaml file '''
  logging.info(f"Exporting {obj}...")

  if config.in_cluster:
    # running inside kubernetes, kubectl does not require kubeconfig or context
    # you will have to configure a service account and permissions for the pod
    cmd = "kubectl get %s -o yaml" % obj
  else:
    # running locally
    cmd = f"kubectl --context {config.artsy_env} get {obj} -o yaml"

  logging.debug(f"Running command: {cmd}")

  data = check_output(cmd, shell=True)

  with open(os.path.join(export_dir, "%s.yaml" % obj), 'w') as f:
    f.write('---\n')
    f.write(data.decode("utf-8"))

def export_and_backup(KUBERNETES_OBJECTS):
  ''' export kubernetes objects to yaml files and optionally back them up to S3 '''
  export_dir = os.path.join(config.local_dir, config.artsy_env)
  mkpath(export_dir)

  logging.info(
    f"Exporting objects from Kubernetes {config.artsy_env} cluster, default namespace, as yaml files, to {export_dir} ..."
  )
  for obj in KUBERNETES_OBJECTS:
    try:
      export(obj, export_dir)
    except CalledProcessError as e:
      logging.critical(f"Failed to export {obj} to yaml: {e} Aborting.")
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

def full_s3_prefix(s3_prefix, cluster_label):
  return f"{s3_prefix}/{cluster_label}"

def prune(context, k8s_cluster, s3_bucket, s3_prefix, keepn, force):
  ''' keep 'keepn' most recent backups and delete the rest '''
  cluster_label = determine_cluster_label(context, k8s_cluster)
  full_prefix = full_s3_prefix(s3_prefix, cluster_label)
  logging.info(f"Pruning backups in s3://{s3_bucket}/{full_prefix}/ ...")
  s3 = S3Interface(s3_bucket, prefix=full_prefix)
  for backup_id in s3.backups()[keepn:]:
    if force:
      s3.delete(backup_id)
      logging.info(f"Deleted {backup_id}")
    else:
      logging.info(f"Would have deleted {backup_id}")
  logging.info("Done.")
