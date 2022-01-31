# add_horizon_block.sh

Utility script to add Artsy's Horizon release block config to a project's `.circleci/config.yml`.

# Requirements:

- yq

  https://github.com/mikefarah/yq

- a file that lists project names and their ids as configured in Horizon

  ```
  $ cat ~/horizon_project_ids.txt 
  vibrations 3
  ...
  ```

- the project's `.circleci/config.yml`:
  - has `orbs:` key
  - has `&only_release` yaml anchor
  - its main workflow is named `build-deploy`
  - it doesn't have a `horizon/block` workflow job
  - it has a `hokusai/deploy-production` workflow job

# How to run it against a project

Say:
- the project is stored in `~/code/project1`
- this script's repo is stored in `~/code/ops-util/hokusai-app-updater`
- project-name-to-id file is stored in `~/tmp/horizon_project_ids.txt`

```
cd ~/code/project1
~/code/ops-util/hokusai-app-updater/update_scripts/add_horizon_block/add_horizon_block.sh ~/tmp/horizon_project_ids.txt
```

# What it does

It edits the project's `.circleci/config.yml` to:

- include Horizon orb with its version harcoded
- include a `horizon/block` job under `workflows`
- make `hokusai/deploy-production` require `horizon/block`

# Caveats

- The script uses `yq` which removes all blank lines.

