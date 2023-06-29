import logging
import os
import requests
import shutil
import sys

from distutils.dir_util import mkpath

import rabbitmq_export_definitions.context

from lib.artsy_s3_backup import ArtsyS3Backup
from rabbitmq_export_definitions.config import config

def export_and_backup():
  full_dir = os.path.join(config.local_dir, config.artsy_env)
  mkpath(full_dir)
  file_name = f"{config.rabbitmq_host}.json"
  output_file = os.path.join(full_dir, file_name)
  export_broker_definition(output_file)
  if config.s3:
    try:
      artsy_s3_backup = ArtsyS3Backup(config.s3_bucket, config.s3_prefix, 'rabbitmq', config.artsy_env, 'json')
      artsy_s3_backup.backup(output_file)
    except:
      raise
    finally:
      logging.info(f"Deleting {config.local_dir} ...")
      shutil.rmtree(config.local_dir)
  else:
    logging.info("Skipping backup to S3. Please delete the local files when done!")

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
  except Exception as e:
    # print custom error message to prevent username/password from being printed
    sys.exit(
      f"Error: Exception encountered"
    )
  if resp.status_code != 200:
    sys.exit(
      f"Error: RabbitMQ returned HTTP status: {resp}"
    )
  logging.info(
    f"Saving RabbitMQ broker definitions to {output_file} ..."
  )
  with open(output_file, 'w') as f:
    f.write(resp.text)
