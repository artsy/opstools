#!/bin/bash

MATCH=<match-pattern>
REPLACE=<replace-pattern>

echo "replacing '$MATCH' with '$REPLACE' in dependabot.yml"

sed -i "s|$MATCH|$REPLACE|" .github/dependabot.yml
