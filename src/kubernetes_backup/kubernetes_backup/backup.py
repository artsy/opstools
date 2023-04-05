import os
import shutil
import sys

import tarfile

from datetime import datetime
from distutils.dir_util import mkpath
from subprocess import check_output, CalledProcessError

from kubernetes_backup.s3 import S3Interface

def backup_to_s3(basedir, export_dir, cluster_label, s3_bucket, s3_prefix):
  ''' back up yamls to S3 '''
  archive_file = os.path.join(basedir, "kubernetes-backup-%s.tar.gz" % cluster_label)
  print("INFO: Writing local archive file: %s" % archive_file)
  with tarfile.open(archive_file, "w:gz") as tar:
    tar.add(export_dir, arcname=os.path.basename(export_dir))

  backup_id = str(datetime.now()).replace(' ', '_')
  print("INFO: Backing up archive file to 's3://%s/%s/%s'" % (s3_bucket, s3_prefix, backup_id))
  s3 = S3Interface(s3_bucket, prefix="%s/%s" % (s3_prefix,cluster_label))
  s3.backup(archive_file, backup_id)

  print("INFO: Deleting local archive file...")
  os.remove(archive_file)
  print("INFO: Deleting %s ..." % export_dir)
  shutil.rmtree(export_dir)

def export(obj, export_dir, context):
  ''' export k8s object into a yaml file '''
  print("INFO: Exporting %s..." % obj)

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

def export_and_backup(context, k8s_cluster, basedir, to_s3, s3_bucket, s3_prefix, KUBERNETES_OBJECTS):
  ''' export kubernetes objects to yaml files and optionally back them up to S3 '''
  if context:
    cluster_label = context
  else:
    cluster_label = k8s_cluster

  export_dir = os.path.join(basedir, cluster_label)
  mkpath(export_dir)

  print("INFO: Exporting objects from Kubernetes cluster '%s', 'default' namespace, as yaml files, to '%s'..." % (cluster_label, basedir))
  for obj in KUBERNETES_OBJECTS:
    try:
      export(obj, export_dir, context)
    except CalledProcessError as e:
      print("Error: exporting %s to yaml: %s" %(obj, e))
      shutil.rmtree(export_dir)
      sys.exit(1)
  print("INFO: Done exporting")

  if to_s3:
    backup_to_s3(basedir, export_dir, cluster_label, s3_bucket, s3_prefix)
  else:
    print("INFO: Skipping backup to S3. Please delete the local files when done!")
