# `update_apps.sh`

A wrapper script for making changes to hokusai-enabled apps en mass.

It loops through project directories, cuts a branch, runs a script that actually makes changes to the project, commits the changes, pushes the branch up to origin (Github), and cuts a PR.

## Setup

### gh

`update_apps.sh` relies on `gh` to interact with Github https API for the PR part. `gh` must be installed and logged-in to Github. See:

- https://github.com/cli/cli
- https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token

The token must have at least these privileges:

- repo
- read:org

Here's how to log in/out of Gihub using `gh`:

```
user@artsy:~$ gh auth status
You are not logged into any GitHub hosts. Run gh auth login to authenticate.
user@artsy:~$
user@artsy:~$ gh auth login
? What account do you want to log into? GitHub.com
- Logging into github.com
? How would you like to authenticate? Paste an authentication token

Tip: you can generate a Personal Access Token here https://github.com/settings/tokens
The minimum required scopes are 'repo' and 'read:org'.
? Paste your authentication token: ****************************************
? Choose default git protocol SSH
- gh config set -h github.com git_protocol ssh
✓ Configured git protocol
✓ Logged in as artsyuser
user@artsy:~$
user@artsy:~$ gh auth status
github.com
  ✓ Logged in to github.com as artsyuser (~/.config/gh/hosts.yml)
  ✓ Git operations for github.com configured to use ssh protocol.
  ✓ Token: *******************

user@artsy:~$ gh auth logout
? Are you sure you want to log out of github.com account 'artsyuser'? Yes
✓ Logged out of github.com account 'artsyuser'
```

## Usage

* Prepare a change script (can be bash, etc.). See [examples](examples/).

* Run `update_apps.sh` to apply changes and push PRs.

```
$ pwd
/home/user/code/opstools/hokusai-app-updater
user@artsy:~/code/opstools/hokusai-app-updater$ ./update_apps.sh
    Usage: ./update_apps.sh path_to_change_script(relative to this dir) path_to_project_list path_to_source_code_root_dir branch_name commit_message(also pr title/body) pr_reviewer(also assignee)
```

- `~/tmp/list`: path to file that lists the projects you wish to change. The list is likely different for different tasks.
```
user@artsy:~/tmp$ cat list
convection
pulse
```

`/home/user/code`: root dir for source code. Each project's source code dir must be under this root dir. For example:
```
user@artsy:~/code/convection$ pwd
/home/user/code/convection
```

When making changes to `convection` for example, the script will go into `/home/user/code/convection`. Therefore, project names in the list must match dir names in source root.

> [!NOTE]
> A checkout of each project _must_ exist in the specified directory, in a clean state, and without a branch matching the specified name. To ensure this is the case, it might be convenient to freshly clone the projects to a new location instead. E.g.:
>
> ```bash
> sed 's|\(.*\)|git@github.com:artsy/\1.git|' ~/code/opstools/src/hokusai-app-updater/examples/replace_deprecated_specs/project_list | xargs -n 1  git clone
> ```

### Examples

```bash
./update_apps.sh examples/replace_deprecated_specs/replace_deprecated_specs.sh examples/replace_deprecated_specs/project_list ~/code deprecations "Replace deprecated k8s specs" joeyAghion artsyjian
```

When making changes with _a high degree of certainty_, you can set the `MERGE_ON_GREEN` environment variable to label pull requests accordingly and save some review labor:

```bash
MERGE_ON_GREEN=1 ./update_apps.sh examples/replace_deprecated_specs/replace_deprecated_specs.sh examples/replace_deprecated_specs/project_list ~/code deprecations "Replace deprecated k8s specs" joeyAghion artsyjian
```
