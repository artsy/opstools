import logging

from datetime import datetime, timedelta, timezone

import list_vault_jwt_expiration.context

from lib.jwt import is_jwt
from lib.util import url_host_port
from lib.vault import Vault


def validate_vault_jwt_expiration(
    vault_host,
    vault_port,
    kvv2_mount_point,
    warn_threshold,
):
    """validate if JWTs in a vault environment will expire within a given threshold (days)"""
    vault_path = "kubernetes/apps"
    vault_client = Vault(
        url_host_port(vault_host, vault_port),
        auth_method="iam",
        kvv2_mount_point=kvv2_mount_point,
        path=vault_path,
    )
    # Dictionary to store the results. We will error if not empty and print the results
    scan_results = {}
    projects_list = vault_client.list(only_valid=False)

    logging.info(f"List of projects: {projects_list}")
    for project in projects_list:
        logging.info(f"Scanning {project}...")
        check_jwt_expiry(
            project,
            vault_host,
            vault_port,
            kvv2_mount_point,
            warn_threshold,
            scan_results,
        )
    if scan_results:
        raise Exception(
            f"The following JWT(s) will expire within {warn_threshold} days:  {scan_results}"
        )
    else:
        logging.info("Scan complete. All JWTs are valid beyond {warn_threshold} days")


def check_jwt_expiry(
    project, vault_host, vault_port, kvv2_mount_point, warn_threshold, scan_results
):
    """check if JWTs for a given project will expire within a given threshold (days)"""
    vault_path = "kubernetes/apps/" + f"{project}"
    vault_client = Vault(
        url_host_port(vault_host, vault_port),
        auth_method="iam",
        kvv2_mount_point=kvv2_mount_point,
        path=vault_path,
    )
    expiring_jwts = {}
    jwt_keys = vault_client.list(match_function=is_jwt, match_type="value")

    for key in jwt_keys:
        logging.info(f"Checking jwt {key} in {project}.")

        metadata = vault_client.read_custom_meta(key)
        expiry_date = metadata["expires_at"] if metadata else None

        if expiry_date is not None:
            current_time = datetime.now(timezone.utc)
            warn_threshold_time = current_time + timedelta(days=warn_threshold)
            warn_threshold_time_iso = warn_threshold_time.isoformat()

            if expiry_date >= warn_threshold_time_iso:
                logging.info(
                    f"JWT {vault_path}{key} will expire within {warn_threshold} days"
                )
                expiring_jwts[key] = expiry_date
            else:
                logging.info(
                    f"JWT {vault_path}{key} is valid for at least {warn_threshold} days"
                )
        else:
            logging.info(
                f"JWT {vault_path}{key} does not have a expires_at field set in custom metadata"
            )
    if expiring_jwts:
        # Vault returns the project name with a trailing slash, so we remove it before using it as the dictionary key
        scan_results[project[:-1]] = expiring_jwts
