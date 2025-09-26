#!/bin/bash
set -e

# USAGE: cd src/hokusai-app-updater/examples/add_github_action && ./run.sh

# NOTE: Paths are relative to the location of this script.
PATH_TO_CHANGE_SCRIPT=""
PATH_TO_PROJECT_LIST="" # Requires newline delimited list with a terminating empty line
PATH_TO_SOURCE_CODE_ROOT_DIR=""
BRANCH_NAME=""
COMMIT_TITLE=""
COMMIT_MESSAGE=""
PR_REVIEWER=
PR_ASSIGNEE=

# If feeling bold add MERGE_ON_GREEN=1 to env to add "Merge On Green" label to PR.
src/hokusai-app-updater/update_apps.sh \
    "$PATH_TO_CHANGE_SCRIPT" \
    "$PATH_TO_PROJECT_LIST" \
    "$PATH_TO_SOURCE_CODE_ROOT_DIR" \
    "$BRANCH_NAME" \
    "$COMMIT_TITLE" \
    "$COMMIT_MESSAGE" \
    "$PR_REVIEWER" \
    "$PR_ASSIGNEE"
