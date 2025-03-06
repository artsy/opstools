import logging
import os

import vault_snapshot.context

from lib.export_backup import backup_to_s3, setup_local_export_dir
from lib.util import url_host_port
from lib.vault import Vault


def take_snapshot(
    local_dir, artsy_env, vault_host, vault_port, vault_role, s3, s3_bucket, s3_prefix
):
    vault_client = Vault(
        url_host_port(vault_host, vault_port), auth_method="iam", role=vault_role
    )
    suffix = "gz"
    export_dir, output_file = setup_local_export_dir(
        local_dir, artsy_env, vault_host, suffix
    )
    logging.info("Taking snapshot...")
    vault_client.take_snapshot(output_file)
    if s3:
        backup_to_s3(
            s3_bucket,
            s3_prefix,
            "vault_snapshot",
            artsy_env,
            suffix,
            output_file,
            export_dir,
        )
    else:
        logging.info("Skipping backup to S3. Please delete the local files when done!")
