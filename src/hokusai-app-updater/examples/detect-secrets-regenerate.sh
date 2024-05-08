#!/bin/bash

# This script can be used to regenerate detect-secrets baselines across projects that use detect-secrets.
# It is intended to be used with update_apps.sh, which will run this script in each projects directory.
# To get a list of codebases which contain .secrets.baseline see https://www.notion.so/artsy/Detect-Secrets-cd11d994dabf45f6a3c18e07acb5431c?pvs=4#9208f19689244b28ad86ae3c5d0143b0

dir=${PWD##*/} # Get the current directory name
scan="detect-secrets scan > .secrets.baseline" # Default scan command
rescan() {
  echo "Re-running detect-secrets scan to add an exclusion filter for the baseline file"
  detect-secrets scan --baseline .secrets.baseline
}

if [ "$dir" == "force" ];
then
  # This is a special case for the force codebase, which has a custom detect-secrets script with numerous exclusions.
  # Instead of including the exclusions in this file, source the script and execute the regen() function.
  source scripts/detect-secrets.sh
  regen
  exit 0
fi

if [ "$dir" == "eigen" ] || [ "$dir" == "energy" ];
then
  # This is a special case for the eigen and energy codebase, which have a custom detect-secrets script with numerous exclusions.
  # Instead of including the exclusions in this file, execute that specific script.
  scripts/detect-secrets/secrets-generate-baseline
  rescan
  exit 0
fi

if [ "$dir" == "gravity" ] || [ "$dir" == "positron" ] || [ "$dir" == "ohm" ] || [ "$dir" == "pulse" ] || [ "$dir" == "volt" ];
then
  scan="detect-secrets scan --exclude-secrets '[a-fA-F0-9]{24}' > .secrets.baseline"
fi

if [ "$dir" == "forque" ] || [ "$dir" == "volt-v2" ];
then
  scan="detect-secrets scan --exclude-files 'src/__generated__/.*\.ts$' > .secrets.baseline"
fi

echo "Executing detect-secrets scan to regenerate the baseline for $dir"
eval $scan
rescan

echo "done"
