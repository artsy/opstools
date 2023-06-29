import os
import shutil
import sys

import logging
import tarfile

from datetime import datetime
from distutils.dir_util import mkpath
from subprocess import check_output, CalledProcessError

from kubernetes_backup.s3 import S3Interface

from lib.artsy_s3_backup import ArtsyS3Backup

def backup_to_s3(basedir, export_dir, cluster_label, s3_bucket, s3_prefix):
  ''' back up yamls to S3 '''
  archive_file = os.path.join(
                   basedir, "kubernetes-backup-%s.tar.gz" % cluster_label
                 )
  logging.info(f"Writing local archive file: {archive_file} ...")
  with tarfile.open(archive_file, "w:gz") as tar:
    tar.add(export_dir, arcname=os.path.basename(export_dir))
  try:
    artsy_s3_backup = ArtsyS3Backup(s3_bucket, s3_prefix, 'k8s', cluster_label, 'tar.gz')
    artsy_s3_backup.backup(archive_file)
  except:
    raise
  finally:
    logging.info(f"Deleting {archive_file} ...")
    os.remove(archive_file)

def determine_cluster_label(context, k8s_cluster):
  ''' determine k8s cluster's name for use as label '''
  if context:
    cluster_label = context
  else:
    cluster_label = k8s_cluster
  return cluster_label

def export(obj, export_dir, context):
  ''' export k8s object into a yaml file '''
  logging.info(f"Exporting {obj}...")

  if context:
    # when running locally
    cmd = "kubectl --context %s get %s -o yaml" % (context,obj)
  else:
    # when running inside kubernetes, don't use kubeconfig or context
    # you will have to configure a service account and permissions for the pod
    cmd = "kubectl get %s -o yaml" % obj
  data = check_output(cmd, shell=True)

  with open(os.path.join(export_dir, "%s.yaml" % obj), 'w') as f:
    f.write('---\n')
    f.write(data.decode("utf-8"))

def export_and_backup(context, k8s_cluster, basedir, s3, s3_bucket, s3_prefix, KUBERNETES_OBJECTS):
  ''' export kubernetes objects to yaml files and optionally back them up to S3 '''
  cluster_label = determine_cluster_label(context, k8s_cluster)
  export_dir = os.path.join(basedir, cluster_label)
  mkpath(export_dir)

  logging.info(
    f"Exporting objects from Kubernetes cluster {cluster_label}, default namespace, as yaml files, to {basedir} ..."
  )
  for obj in KUBERNETES_OBJECTS:
    try:
      export(obj, export_dir, context)
    except CalledProcessError as e:
      logging.critical(f"Failed to export {obj} to yaml: {e} Aborting.")
      shutil.rmtree(export_dir)
      sys.exit(1)
  logging.info("Done exporting")

  if s3:
    try:
      backup_to_s3(basedir, export_dir, cluster_label, s3_bucket, s3_prefix)
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
