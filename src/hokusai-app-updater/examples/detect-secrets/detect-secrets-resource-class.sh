#!/bin/bash

_MATCH='      - image: artsy/detect-secrets:ci # pragma: allowlist secret'

REPLACE='      - image: artsy/detect-secrets:ci # pragma: allowlist secret\n    resource_class: small'

echo "replacing '$_MATCH' with '$REPLACE' in .circleci/config.yml"

sed -i '' -e "s|$_MATCH|$REPLACE|" .circleci/config.yml

echo "done"
