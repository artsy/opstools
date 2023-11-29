import logging
import os
import requests
import shutil

from distutils.dir_util import mkpath

import rabbitmq_export.context

from lib.artsy_s3_backup import ArtsyS3Backup


def export_and_backup(
  local_dir,
  artsy_env,
  rabbitmq_host,
  rabbitmq_user,
  rabbitmq_pass,
  s3,
  s3_bucket,
  s3_prefix
):
  logging.info(
    'Exporting and backing up RabbitMQ broker definitions...'
  )
  export_dir = os.path.join(local_dir, artsy_env)
  mkpath(export_dir)
  file_name = f"{rabbitmq_host}.json"
  output_file = os.path.join(export_dir, file_name)
  export_broker_definition(
    output_file, rabbitmq_host, rabbitmq_user, rabbitmq_pass
  )
  if s3:
    try:
      artsy_s3_backup = ArtsyS3Backup(
        s3_bucket,
        s3_prefix,
        'rabbitmq',
        artsy_env,
        'json'
      )
      artsy_s3_backup.backup(output_file)
    except:
      raise
    finally:
      logging.info(f"Deleting {export_dir} ...")
      shutil.rmtree(export_dir)
  else:
    logging.info(
      "Skipping backup to S3. Please delete the local files when done!"
    )
  logging.info(
    'Done exporting and backing up RabbitMQ broker definitions...'
  )

def export_broker_definition(
  output_file, rabbitmq_host, rabbitmq_user, rabbitmq_pass
):
  scheme = 'https://'
  user_pass = f"{rabbitmq_user}:{rabbitmq_pass}@"
  host_path = f"{rabbitmq_host}/api/definitions"
  url = scheme + user_pass + host_path
  try:
    logging.info(
      f"Sending request to {scheme}<FILTERED>:<FILTERED>@{host_path} ..."
    )
    resp = requests.get(url)
  except:
    # print custom error message
    # to prevent username/password from being printed
    raise Exception
  if resp.status_code != 200:
    raise Exception(f"RabbitMQ returned HTTP status: {resp}")
  logging.info(
    f"Saving RabbitMQ broker definitions to {output_file} ..."
  )
  with open(output_file, 'w') as f:
    f.write(resp.text)
