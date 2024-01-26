import logging
import os
import requests

import rabbitmq_export.context

from lib.util import (
  backup_to_s3,
  write_file
)


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
  suffix = 'json'
  export_dir, output_file = setup_local_export_dir(
    local_dir, artsy_env, rabbitmq_host, suffix
  )
  logging.info('Exporting broker definitions...')
  export_broker_definition(
    output_file, rabbitmq_host, rabbitmq_user, rabbitmq_pass
  )
  if s3:
    backup_to_s3(
      s3_bucket,
      s3_prefix,
      'rabbitmq',
      artsy_env,
      suffix,
      output_file,
      export_dir
    )
  else:
    logging.info(
      "Skipping backup to S3. Please delete the local files when done!"
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
  write_file(output_file, resp.text)
