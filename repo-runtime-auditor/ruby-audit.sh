#!/bin/bash

GEMFILE_REGEX="ruby \'(([0-9]?[0-9]\.)){0,2}([0-9]?[0-9])\'"
DOT_RUBY_VERSION_REGEX="(([0-9]?[0-9]\.)){0,2}([0-9]?[0-9])"

PROJECT=$1

function file_download() {
  curl -s -o output.txt \
    -H "Authorization: token "$GITHUB_READ_TOKEN \
    "https://raw.githubusercontent.com/artsy/$PROJECT/main/$1" 
}

function file_validator() {
  file_download "$1"
  grep "404: Not Found" output.txt > /dev/null
}

function file_search() {
  grep -Eo "$1" output.txt
}

# Check for existence of files that would include the ruby version.
# Order matters here, as we aren't currently validating if an existing 
# file has the ruby version.
#
# For example: a Gemfile may exist in a repo but just point 
# to the .ruby-version. Currently this would result in use 
# skipping the grep for .ruby-version.
if ! file_validator ".ruby-version"; then
  result=$(file_search "$DOT_RUBY_VERSION_REGEX")
elif ! file_validator "Gemfile"; then
  result=$(file_search "$GEMFILE_REGEX")
fi

if [ -n "$result" ]; then
  echo "###### $PROJECT ######"
  echo $result
  echo
fi
