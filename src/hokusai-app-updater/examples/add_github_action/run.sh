#!/bin/bash
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"

# Check if config.json exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: config.json not found. Please copy config.example.json to config.json and update the values."
    exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed. Please install jq first."
    exit 1
fi

# Validate required fields in config.json
REQUIRED_FIELDS=("pathToSourceCodeRootDir" "branchName" "deleteBranchIfExists" "commitMessage" "prDescription" "prReviewer" "prAssignee" "actionConfigFile" "projectList")
for FIELD in "${REQUIRED_FIELDS[@]}"; do
    if [[ -z "$(jq -r --arg field "$FIELD" '.[$field]' "$CONFIG_FILE")" || "$(jq -r --arg field "$FIELD" '.[$field]' "$CONFIG_FILE")" == "null" ]]; then
        echo "Error: '$FIELD' is required in config.json but is missing or empty."
        exit 1
    fi
done

# If feeling bold add MERGE_ON_GREEN=1 to env to add "Merge On Green" label to PR.
"$SCRIPT_DIR/update_apps.sh" \
    "$SCRIPT_DIR/copy-action.sh" \
    "$(jq -r '.projectList' "$CONFIG_FILE" | jq -r 'join("\n")')" \
    "$(jq -r '.pathToSourceCodeRootDir' "$CONFIG_FILE")" \
    "$(jq -r '.branchName' "$CONFIG_FILE")" \
    "$(jq -r '.commitMessage' "$CONFIG_FILE")" \
    "$(jq -r '.prDescription' "$CONFIG_FILE")" \
    "$(jq -r '.prReviewer' "$CONFIG_FILE")" \
    "$(jq -r '.prAssignee' "$CONFIG_FILE")" \
    "$(jq -r '.actionConfigFile' "$CONFIG_FILE")" \
    "$(jq -r '.deleteBranchIfExists' "$CONFIG_FILE")" 
