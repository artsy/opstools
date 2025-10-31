#!/bin/bash

set -e

ARGUMENT_COUNT=8

function check_input() {
  if (( $# < $ARGUMENT_COUNT ))
  then
    usage
    exit 1
  fi
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
  git --no-pager diff
  read -p "Enter y or Y to proceed, s or S to skip, any other input exit script: " -n 1 -r </dev/tty
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]
  then
    echo "Applying changes..."
  elif [[ $REPLY =~ ^[Ss]$ ]]
  then
    # exit function but continue executing the script
    return
  else
    exit 1
  fi

  echo "### commit changes ###"
  git add .
  git commit -m "$TITLE" --no-verify
  echo "### push to origin ###"
  git push -f --set-upstream origin "$BRANCH" --no-verify

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
  eval "gh pr create --title \"$TITLE\" --body \"$BODY\" --reviewer \"$REVIEWER\" --assignee \"$ASSIGNEE\" $LABEL_ARG"
}

check_input "$@"

# Absolute path to the script that makes the desired changes.
SCRIPT=$1

# path to file that lists projects to be operated on.
PROJECT_LIST=$2

# path to dir that holds dirs of all projects.
# should be absolute path.
CODE_DIR_ROOT=$3

# name of github branch to make changes under.
BRANCH=$4

# title of PR and commit message.
TITLE=$5

# commit message.
BODY=$6

# reviewer (user or team) for pr.
REVIEWER=$7

# assignee for pr.
ASSIGNEE=$8

COUNT=1

while read -r PROJECT;
do
  echo "---------------- #$COUNT: $PROJECT -------------------------"

  # check if project exists, if not, clone it with GH CLI, if user wants it to be cloned
  if [ ! -d "$CODE_DIR_ROOT/$PROJECT" ]
  then
    echo "### $PROJECT does not exist in $CODE_DIR_ROOT ###"
    read -p "Would you like to clone it from GitHub? Enter y or Y to proceed: " -n 1 -r </dev/tty
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
      echo "Cloning $PROJECT into $CODE_DIR_ROOT"
      gh repo clone "artsy/$PROJECT" "$CODE_DIR_ROOT/$PROJECT"
    else
      echo "Skipping $PROJECT"
      continue
    fi
  fi

  # allow user to skip project
  echo "### Operate on $PROJECT? ###"
  read -p "Enter y or Y to proceed: " -n 1 -r </dev/tty
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]
  then
    continue
  fi

  WORKDIR="$CODE_DIR_ROOT/$PROJECT"
  cd "$WORKDIR"
  echo "### Operating in directory: $WORKDIR ###"
  prep "$BRANCH"

  echo "### run script ###"
  # pass on to script argument#9 and on
  $SCRIPT_DIR/$SCRIPT "$CODE_DIR_ROOT" "$PROJECT" "${@:9}"

  # commit if there are changes
  changes=$(git status -s)
  if [ ! -z "$changes" ]
  then
    commit "$BRANCH"
  else
    echo "no changes"
  fi

  COUNT=$(( $COUNT + 1 ))
done <<< "$PROJECT_LIST"
