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

  # Determine default branch (main or master)
  if git show-ref --verify --quiet refs/heads/main || git show-ref --verify --quiet refs/remotes/origin/main; then
    DEFAULT_BRANCH="main"
  else
    DEFAULT_BRANCH="master"
  fi

  echo "### checkout $DEFAULT_BRANCH ###"
  git checkout "$DEFAULT_BRANCH"
  echo "### rebase from origin/$DEFAULT_BRANCH ###"
  git pull --rebase origin "$DEFAULT_BRANCH"
  echo "### checkout $BRANCH branch ###"
  if [ "$DELETE_BRANCH_IF_EXISTS" = true ] ; then
    if git show-ref --verify --quiet refs/heads/"$BRANCH"; then
      echo "Branch $BRANCH exists, deleting..."
      git branch -D "$BRANCH"
    fi
  fi

  git checkout -B "$BRANCH"
}

function commit() {
  BRANCH=$1
  WORKFLOW_FILE=$2

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
  git add -f ".github/workflows/$WORKFLOW_FILE"
  git commit -m "$TITLE" --no-verify
  echo "### push to origin ###"
  git push -f --set-upstream origin "$BRANCH" --no-verify

  echo "### open or update PR ###"

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

  # Check if PR already exists for this branch
  EXISTING_PR=$(gh pr list --head "$BRANCH" --json number --jq '.[0].number' 2>/dev/null || echo "")

  if [[ -n "$EXISTING_PR" ]]; then
    echo "PR #$EXISTING_PR already exists for branch $BRANCH, updating it..."
    gh pr edit "$EXISTING_PR" --title "$TITLE" --body "$BODY"
    # Add reviewer and assignee if they don't already exist
    gh pr edit "$EXISTING_PR" --add-reviewer "$REVIEWER" --add-assignee "$ASSIGNEE" 2>/dev/null || true
    if [[ -n "${MERGE_ON_GREEN}" ]]; then
      gh pr edit "$EXISTING_PR" --add-label "Merge On Green" 2>/dev/null || true
    fi
    echo "Updated PR #$EXISTING_PR"
  else
    echo "Creating new PR..."
    eval "gh pr create --title \"$TITLE\" --body \"$BODY\" --reviewer \"$REVIEWER\" --assignee \"$ASSIGNEE\" $LABEL_ARG"
  fi
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

# workflow filename.
WORKFLOW_FILE=$9

# delete file if exists
DELETE_BRANCH_IF_EXISTS=${10}

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
    commit "$BRANCH" "$WORKFLOW_FILE"
  else
    echo "no changes"
  fi

  COUNT=$(( $COUNT + 1 ))
done <<< "$PROJECT_LIST"
