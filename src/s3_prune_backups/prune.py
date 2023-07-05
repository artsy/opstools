# initialize the app
from s3_prune_backups.config import config

from s3_prune_backups.prune_backups import (
  prune
)

if __name__ == "__main__":

  prune()
