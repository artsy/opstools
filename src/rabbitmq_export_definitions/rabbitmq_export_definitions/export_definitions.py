import logging
import os
import requests
import shutil

from distutils.dir_util import mkpath

import rabbitmq_export_definitions.context

from lib.artsy_s3_backup import ArtsyS3Backup
from lib.s3_interface import S3Interface
from rabbitmq_export_definitions.config import config

def export_and_backup():
  logging.info(
    'Exporting and backing up RabbitMQ broker definitions...'
  )
  export_dir = os.path.join(config.local_dir, config.artsy_env)
  mkpath(export_dir)
  file_name = f"{config.rabbitmq_host}.json"
  output_file = os.path.join(export_dir, file_name)
  export_broker_definition(output_file)
  if config.s3:
    try:
      s3_interface = S3Interface()
      artsy_s3_backup = ArtsyS3Backup(
        config.s3_bucket,
        config.s3_prefix,
        'rabbitmq',
        config.artsy_env,
        'json',
        s3_interface
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

def export_broker_definition(output_file):
  scheme = 'https://'
  user_pass = f"{config.rabbitmq_user}:{config.rabbitmq_pass}@"
  host_path = f"{config.rabbitmq_host}/api/definitions"
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
