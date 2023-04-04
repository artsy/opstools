#!/usr/bin/env bash

# edit a project's .circleci/config.yml
# change version of artsy-managed orbs from x.y.z -> volatile
#
# example:
#
# orbs:                               
#  hokusai: artsy/hokusai@0.9.0                                               
#
# becomes
#
# orbs:
#  hokusai: artsy/hokusai@volatile        

sed -i 's|\(^.*: artsy/.*\)@[0-9]*\.[0-9]*\.[0-9]*$|\1@volatile|' .circleci/config.yml
