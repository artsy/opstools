import logging

# initialize the app
from rabbitmq_export_definitions.config import config

from rabbitmq_export_definitions.export_definitions import \
  export_and_backup

if __name__ == "__main__":

  logging.info(
    'Exporting RabbitMQ broker defiitions ...'
  )
  export_and_backup()
  logging.info(
    'Done exporting RabbitMQ broker defiitions.'
  )
