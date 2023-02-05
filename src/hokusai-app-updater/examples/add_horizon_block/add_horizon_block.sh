#!/bin/bash

ORIGINAL_FILE='./.circleci/config.yml'

DATESTR=$(date +%Y%m%d%H%M%S)
TMP_DIR="./tmp.$DATESTR"
WORKING_FILE="$TMP_DIR/working.yml"

mkdir $TMP_DIR

cp $ORIGINAL_FILE $WORKING_FILE

# get Horizon's id for the project
PROJ_ID_FILE=$1
PWD=$(pwd)
PROJ_NAME=$(basename $PWD)
PROJ_ID=$(grep "$PROJ_NAME " $PROJ_ID_FILE | awk '{print $2}')

# add horizon orb
yq e -i '.orbs.horizon = "artsy/release@0.0.1"' $WORKING_FILE

# add horizon/block workflow job, placeholder for project id
yq e -i '.workflows.build-deploy.jobs += {"horizon/block": {"context": "horizon", "project_id": "<proj-id>"}}' $WORKING_FILE

# add alias under horizon/block
sed -i 's|horizon/block:$|horizon/block:\n          <<: *only_release|' $WORKING_FILE

# see if hokusai/deploy-production already has requires
REQUIRES=$(yq e '.workflows.build-deploy.jobs[] |
                 select(has("hokusai/deploy-production"))
                 ["hokusai/deploy-production"] |
                 has("requires")' $WORKING_FILE)

if [[ $REQUIRES == "true" ]]
then
  # append to requires
  yq e -i '(.workflows.build-deploy.jobs[] |
            select(has("hokusai/deploy-production"))
            ["hokusai/deploy-production"].requires) += ["horizon/block"]' $WORKING_FILE
else
  # add requires
  yq e -i '(.workflows.build-deploy.jobs[] |
            select(has("hokusai/deploy-production"))
            ["hokusai/deploy-production"].requires)
            = ["horizon/block"]' $WORKING_FILE
fi

# our .circleci/config.yml uses yaml aliases, example:
#
#      - hokusai/deploy-production:
#          <<: *only_release
#
# for some reason when processing the file, yq modifies the alias to this:
#
#      - hokusai/deploy-production:
#          !!merge  <<: *only_release
#
# undo that
sed -i 's/!!merge //g' $WORKING_FILE

# fill in proj id placeholder
sed -i "s/<proj-id>/$PROJ_ID/g" $WORKING_FILE

# overwrite original circleci config file with the new file
mv $WORKING_FILE $ORIGINAL_FILE

# clean up
rm -rf $TMP_DIR
