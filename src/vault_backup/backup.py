import os

import json
import logging

from collections import defaultdict

from lib.encrypt import symmetric_encrypt
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
    encryption_key,
    encryption_iv,
):
    """Encrypts Vault secrets using AES256 and exports them to S3."""
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
    secrets = defaultdict(lambda: {})
    for app in apps:
        app_name = app.strip("/")
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

    logging.info("Encrypting secrets...")
    cipher_text = symmetric_encrypt(encryption_key, encryption_iv, secrets_json)

    output_file = os.path.join(local_dir, "secrets.enc")
    logging.info(f"Writing encrypted secrets to local file {output_file} ...")
    write_file(output_file, cipher_text, data_format="binary")

    if s3:
        s3_sub_prefix = "vault_backup"
        try:
            logging.info(
                f"Backing up secrets to {s3_bucket} bucket and {s3_prefix}/{s3_sub_prefix} prefix"
            )
            backup_to_s3(
                s3_bucket,
                s3_prefix,
                s3_sub_prefix,
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
