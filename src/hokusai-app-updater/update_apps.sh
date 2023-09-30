#!/bin/bash

set -e

ARGUMENT_COUNT=7

function check_input() {
  if (( $# < $ARGUMENT_COUNT ))
  then
    usage
    exit 1
  fi
}

function usage() {
  cat << EOF
    Usage: $0 path_to_change_script(relative to this dir) path_to_project_list path_to_source_code_root_dir branch_name commit_message(also pr title/body) pr_assignee(user or team) pr_reviewer(user) <extra arguments to pass to the change script itself>...
EOF
}

function prep() {
  BRANCH=$1

  echo "### stash ###"
  git stash
  echo "### git fetch ###"
  git fetch
  echo "### checkout main ###"
  git checkout main
  echo "### rebase from origin/main ###"
  git pull --rebase origin main
  echo "### checkout $BRANCH branch ###"
  git checkout -b "$BRANCH"
}

function commit() {
  BRANCH=$1

  echo "### confirm changes ###"
  git diff
  read -p "Enter y or Y to proceed: " -n 1 -r </dev/tty
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]
  then
      exit 1
  fi

  echo "### commit changes ###"
  git commit -am "$MSG" --no-verify
  echo "### push to origin ###"
  git push --set-upstream origin "$BRANCH" --no-verify

  echo "### open PR ###"

  # check whether you are logged into github https api.
  # command exits 0 if yes, 1 if not.
  # assumes script is run with set -e, so script exits if 1.
  gh auth status

  LABEL_ARG=""
  # If specified, ensure "Merge On Green" label exists and has expected capitalization
  if [[ -n "${MERGE_ON_GREEN}" ]]
  then
    gh label edit "merge on green" --name "Merge On Green" || gh label create "Merge On Green" --color "247A38" --description "Merge this PR when all statuses are green"
    LABEL_ARG='--label "Merge On Green"'
  fi
  eval "gh pr create --title \"$MSG\" --body \"$MSG\" --reviewer \"$REVIEWER\" --assignee \"$ASSIGNEE\" $LABEL_ARG"
}

check_input "$@"

# dir of this script.
SCRIPT_DIR=$(pwd)

# path to the script that makes the desired changes. relative to SCRIPT_DIR.
SCRIPT=$1

# path to file that lists projects to be operated on.
PROJECT_LIST=$2

# path to dir that holds dirs of all projects.
# should be absolute path.
SRC_ROOT=$3

# name of github branch to make changes under.
BRANCH=$4

# commit message. will be title of PR as well.
MSG=$5

# reviewer (user or team) for pr.
REVIEWER=$6

# assignee for pr.
ASSIGNEE=$7

COUNT=1

while read PROJECT
do
  echo "---------------- #$COUNT -------------------------"
  WORKDIR="$SRC_ROOT/$PROJECT"
  cd "$WORKDIR"
  echo "### Operating in directory: $WORKDIR ###"
  prep "$BRANCH"

  cd "$WORKDIR"
  echo "### run script ###"
  # pass on to script argument#8 and on
  $SCRIPT_DIR/$SCRIPT "${@:8}"

  cd "$WORKDIR"
  commit "$BRANCH"

  COUNT=$(( $COUNT + 1 ))
done <$PROJECT_LIST
