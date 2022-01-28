#!/bin/bash

NEW_PG_VERSION=<new-pg-version>

echo "bump pg version to $NEW_PG_VERSION in development.yml and test.yml"

sed -i "s|image: postgres.*$|image: postgres:$NEW_PG_VERSION-alpine|" hokusai/development.yml
sed -i "s|image: postgres.*$|image: postgres:$NEW_PG_VERSION-alpine|" hokusai/test.yml

