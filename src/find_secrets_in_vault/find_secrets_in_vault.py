#!/usr/bin/env python3
"""
Vault Secrets Search Script

This script searches for a specific term in all Vault secrets.

Usage:
    python find_secrets_in_vault.py <search_term>
    
Environment Variables (required):
    VAULT_ADDR: The Vault address (hostname:port)
    VAULT_KVV2_MOUNT_POINT: The KVv2 mount point
    VAULT_PATH: The secret path

Arguments:
    search_term: the text to search for in secret values

Example:
    # connect to VPN (artsy specific)
    # download .env.shared for env vars and set them (artsy specific)
    export VAULT_ADDR=https://foo.example.com:1234
    export VAULT_KVV2_MOUNT_POINT=foo
    export VAULT_PATH=/foo/bar
    python find_secrets_in_vault.py "database_credential"
    python find_secrets_in_vault.py "api_key"

The script will automatically:
- Connect to Vault using the specified vault address
- Login to Vault using AWS authentication (if not already authenticated)
- Search through all vault secrets for the term
"""

import subprocess
import sys
import os

if len(sys.argv) < 2:
    print("Usage: find_secrets_in_vault.py <search_term>")
    print("Make sure to set VAULT_ADDR VAULT_KVV2_MOUNT_POINT and VAULT_PATH environment variables.")
    sys.exit(1)

to_find = sys.argv[1]

required_vars = ['VAULT_ADDR', 'VAULT_KVV2_MOUNT_POINT', 'VAULT_PATH']
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

vault_kvv2_mount_point = os.environ.get('VAULT_KVV2_MOUNT_POINT')
vault_path = os.environ.get('VAULT_PATH')

print("Checking Vault authentication status...")
try:
    subprocess.run("vault token lookup > /dev/null 2>&1", shell=True, check=True)
    print("Already authenticated to Vault.")
except subprocess.CalledProcessError:
    print("Not authenticated. Attempting to login to Vault...")
    try:
        subprocess.run("vault login -method=aws", shell=True, check=True)
        print("Successfully logged into Vault.")
    except subprocess.CalledProcessError:
        print(f"Failed to login to Vault. Please ensure vault is configured and you are connected to the correct VPN (artsy specific).")
        sys.exit(1)

def run_command(command):
    return (
        subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        .stdout.decode()
        .splitlines()
    )

projects = run_command(f"vault kv list -mount {vault_kvv2_mount_point} {vault_path}/")[2:]
for project in projects:
    print(f"Checking values for {project}...")
    keys = run_command(f"vault kv list -mount {vault_kvv2_mount_point} {vault_path}/{project}")[2:]
    for key in keys:
        value = run_command(f"vault kv get -mount {vault_kvv2_mount_point} {vault_path}/{project}{key}")[
            -1
        ]
        if to_find in value:
            print(f"Found matching value in {project} ({key}).")
