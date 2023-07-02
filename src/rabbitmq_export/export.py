# initialize the app
from rabbitmq_export.config import config

from rabbitmq_export.export import (
  export_and_backup
)

if __name__ == "__main__":

  export_and_backup()
