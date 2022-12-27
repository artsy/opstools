#!/bin/bash


# Use GitHub cli to get a list of all repos that aren't archived
gh repo list artsy --limit 400 --json name --json isArchived --jq '.[] | select(.isArchived == false).name' > projects.txt

while read PROJECT
do
  if [ "$1" == "node" ]; then
    ./node-audit.sh $PROJECT
  elif [ "$1" == "ruby" ]; then
    ./ruby-audit.sh $PROJECT
  fi
done < projects.txt