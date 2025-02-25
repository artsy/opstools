import os

import json
import logging

from lib.export_backup import backup_to_s3, write_file
from lib.util import url_host_port
from lib.vault import Vault


def backup_secrets(
    artsy_env,
    vault_host,
    vault_port,
    kvv2_mount_point,
    local_dir,
    s3,
    s3_bucket,
    s3_prefix,
):
    """export secrets"""
    logging.info("Discovering k8s app secrets...")
    vault_path = "kubernetes/apps/"
    vault_client = Vault(
        url_host_port(vault_host, vault_port),
        auth_method="iam",
        kvv2_mount_point=kvv2_mount_point,
        path=vault_path,
    )
    apps = vault_client.list(only_valid=False)
    logging.debug(f"Found apps: {apps}")
    secrets = {}
    for app in apps:
        app_name = app.strip("/")
        secrets[app_name] = {}
        logging.debug(f"Reading vars for app: {app_name}...")
        vault_path = "kubernetes/apps/" + f"{app}/"
        vault_client = Vault(
            url_host_port(vault_host, vault_port),
            auth_method="iam",
            kvv2_mount_point=kvv2_mount_point,
            path=vault_path,
        )
        vars = vault_client.list()
        logging.debug(f"Found vars: {vars}")
        for var in vars:
            secrets[app_name][var] = vault_client.get(var)

    secrets_json = json.dumps(secrets)
    output_file = os.path.join(local_dir, "secrets.txt")
    logging.info("Writing secrets to local file {output_file} ...")
    write_file(output_file, secrets_json)

    if s3:
        try:
            logging.info(
                f"Backing up secrets to {s3_bucket} bucket and {s3_prefix}/vault_ascii prefix"
            )
            backup_to_s3(
                s3_bucket,
                s3_prefix,
                "vault_ascii",
                artsy_env,
                "txt",
                output_file,
                local_dir,
                cleanup=False,
            )
        except:
            raise
        finally:
            logging.info(f"Deleting {output_file} ...")
            os.remove(output_file)
    else:
        logging.info(
            f"Skipping backup to S3. Please delete local file {output_file} when done!"
        )
