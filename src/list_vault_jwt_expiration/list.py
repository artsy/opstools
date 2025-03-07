import argparse
import logging
import os

import context

from utils import validate_vault_jwt_expiration
from lib.logging import setup_logging
from lib.validations import hostname_agrees_with_artsy_environment


def parse_args():
    """parse command line args"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            "Evaluates the expiration of JWTs in a given Vault environment and errors if any are going to expire within a given threshold"
        ),
    )
    parser.add_argument(
        "artsy_env", choices=["staging", "production"], help="artsy environment"
    )
    parser.add_argument(
        "--warn_threshold",
        default=30,
        type=int,
        help="The number of days before expiration to warn about",
    )
    parser.add_argument(
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="log level",
    )
    return parser.parse_args()


def parse_env():
    """parse env vars"""
    vault_host = os.environ.get("VAULT_HOST")
    vault_port = os.environ.get("VAULT_PORT")
    vault_role = os.environ.get("VAULT_ROLE")
    kvv2_mount_point = os.environ.get("VAULT_KVV2_MOUNT_POINT")
    return vault_host, vault_port, vault_role, kvv2_mount_point


def validate(artsy_env, vault_host, vault_port):
    """validate config obtained from env and command line"""
    if not (vault_host and vault_port):
        raise Exception(
            "The following environment variables must be specified: "
            + "VAULT_HOST, "
            + "VAULT_PORT"
        )
    if not hostname_agrees_with_artsy_environment(vault_host, artsy_env):
        raise Exception(
            f"Hostname {vault_host} does not agree with environment {artsy_env}"
        )


if __name__ == "__main__":

    args = parse_args()
    artsy_env, loglevel, warn_threshold = (
        args.artsy_env,
        args.loglevel,
        args.warn_threshold,
    )
    setup_logging(eval("logging." + loglevel))
    vault_host, vault_port, vault_role, kvv2_mount_point = parse_env()
    validate(artsy_env, vault_host, vault_port)
    validate_vault_jwt_expiration(
        vault_host,
        vault_port,
        vault_role,
        kvv2_mount_point,
        warn_threshold,
    )
