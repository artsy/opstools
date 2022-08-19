#!/bin/bash

MATCH=artsy/detect-secrets:<old-version>
REPLACE=artsy/detect-secrets:<new-version>

echo "replacing '$MATCH' with '$REPLACE' in .circleci/config.yml"

sed -i "s|$MATCH|$REPLACE|" .circleci/config.yml

echo "done"
