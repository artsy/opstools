#!/bin/bash

# This example script can be used to regenerate detect-secrets baselines across codebases.
# To get a list of codebases which include a baseline file, see https://www.notion.so/artsy/Detect-Secrets-cd11d994dabf45f6a3c18e07acb5431c?pvs=4#9208f19689244b28ad86ae3c5d0143b0

dir=${PWD##*/} # Get the current directory name
scan="detect-secrets scan > .secrets.baseline" # Default scan command
rescan() {
  echo "Re-running detect-secrets scan to add an exclusion filter for the baseline file"
  detect-secrets scan --baseline .secrets.baseline
}

if [ "$dir" == "force" ];
then
  # Force codebase has a script which specifies project specific exclusions for configuring filters.
  # Instead of including the exclusions in this file, source the script and execute the regen function.
  source scripts/detect-secrets.sh
  regen
  echo "done"
  exit 0
elif [ "$dir" == "eigen" ] || [ "$dir" == "energy" ];
then
  # Eigen and energy codebases (like Force) have a script with exclusions for configuring filters.
  # Instead of including the exclusions in this file, execute that specific script.
  scripts/detect-secrets/secrets-generate-baseline
  rescan
  echo "done"
  exit 0
elif [ "$dir" == "gravity" ] || [ "$dir" == "positron" ] || [ "$dir" == "ohm" ] || [ "$dir" == "volt" ];
then
  scan="detect-secrets scan --exclude-secrets '[a-fA-F0-9]{24}' > .secrets.baseline"
elif [ "$dir" == "pulse" ];
then
  scan="detect-secrets scan --exclude-secrets '[a-fA-F0-9]{24}' --exclude-lines 'W/\"[!#-\\x7E]*\"' > .secrets.baseline"
elif [ "$dir" == "forque" ] || [ "$dir" == "volt-v2" ];
then
  scan="detect-secrets scan --exclude-files 'src/__generated__/.*\.ts$' > .secrets.baseline"
fi

echo "Executing detect-secrets scan to regenerate the baseline for $dir"
eval $scan
rescan
echo "done"
