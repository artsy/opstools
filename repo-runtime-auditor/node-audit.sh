
#!/bin/bash

DOCKERFILE_REGEX="node[:-]?(([0-9]?[0-9]\.)){0,2}([0-9]?[0-9])"

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

if ! file_validator "Dockerfile"; then
  RES=$(file_search "$DOCKERFILE_REGEX")
fi

if [ -n "$RES" ]; then
  echo "###### $PROJECT ######"
  echo $RES
  echo
fi