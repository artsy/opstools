import os

import argparse
import logging

import context

from backup import backup_secrets
from lib.logging import setup_logging


def parse_args():
    """parse command line args"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=("Backup Vault secrets"),
    )
    parser.add_argument(
        "artsy_env",
        choices=["staging", "production"],
        help="the artsy environment of Vault instance",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="log level",
    )
    parser.add_argument(
        "--s3", action="store_true", help="indicates to save backup to S3"
    )
    return parser.parse_args()


def parse_env():
    """parse env vars"""
    vault_host = os.environ.get("VAULT_HOST")
    vault_port = os.environ.get("VAULT_PORT")
    kvv2_mount_point = os.environ.get("VAULT_KVV2_MOUNT_POINT")

    # local dir to store exported secrets
    local_dir = os.environ.get("VAULT_BACKUP_LOCAL_DIR")

    s3_bucket = os.environ.get("VAULT_BACKUP_S3_BUCKET", "")
    s3_prefix = os.environ.get("VAULT_BACKUP_S3_PREFIX", "dev")

    encryption_key = os.environ.get("VAULT_BACKUP_ENCRYPTION_KEY", "")
    encryption_iv = os.environ.get("VAULT_BACKUP_ENCRYPTION_IV", "")

    return (
        vault_host,
        vault_port,
        kvv2_mount_point,
        local_dir,
        s3_bucket,
        s3_prefix,
        encryption_key,
        encryption_iv,
    )


def validate(
    vault_host, vault_port, local_dir, s3, s3_bucket, encryption_key, encryption_iv
):
    """validate config obtained from env and command line"""
    if not (
        vault_host and vault_port and local_dir and encryption_key and encryption_iv
    ):
        raise Exception(
            "The following environment variables must be specified: "
            + "VAULT_HOST, "
            + "VAULT_PORT, "
            + "VAULT_BACKUP_LOCAL_DIR, "
            + "VAULT_BACKUP_ENCRYPTION_KEY, "
            + "VAULT_BACKUP_ENCRYPTION_IV"
        )
    if s3 and not s3_bucket:
        raise Exception("VAULT_BACKUP_S3_BUCKET must be specified in the environment.")


if __name__ == "__main__":

    args = parse_args()
    artsy_env, log_level, s3 = (args.artsy_env, args.log_level, args.s3)
    setup_logging(eval("logging." + log_level))
    (
        vault_host,
        vault_port,
        kvv2_mount_point,
        local_dir,
        s3_bucket,
        s3_prefix,
        encryption_key,
        encryption_iv,
    ) = parse_env()
    validate(
        vault_host, vault_port, local_dir, s3, s3_bucket, encryption_key, encryption_iv
    )

    logging.info(f"Backup will be stored locally in {local_dir}")
    if s3:
        logging.info(
            f"Backup will be stored in S3 in {s3_bucket} bucket under {s3_prefix} prefix."
        )

    backup_secrets(
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
    )
