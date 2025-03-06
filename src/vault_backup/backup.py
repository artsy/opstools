import os

import json
import logging

from collections import defaultdict
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

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
    algorithm = algorithms.AES256(bytes.fromhex(encryption_key))
    mode = modes.CTR(bytes.fromhex(encryption_iv))
    cipher = Cipher(algorithm, mode)
    encryptor = cipher.encryptor()
    cipher_text = encryptor.update(bytes(secrets_json, "utf-8")) + encryptor.finalize()

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
