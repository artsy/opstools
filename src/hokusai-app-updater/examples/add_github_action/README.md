# Add GitHub Action

This script automates adding or updating GitHub Actions workflow files across multiple projects.

## Prerequisites

- `jq` - JSON processor for parsing configuration
  ```bash
   # check if jq is installed (most Artsy machines should have it)
   jq --version

   # install jq if not present
   brew install jq
  ```

## Setup

1. Copy the example configuration:
   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` with your values:
   ```json
   {
     "projectList": ["project-1", "project-2"],
     "pathToSourceCodeRootDir": "/path/to/your/code",
     "branchName": "add-github-action",
     "commitMessage": "chore: add GitHub Action workflow",
     "prDescription": "Add automated workflow for CI/CD",
     "prReviewer": "github-username",
     "prAssignee": "github-username",
     "actionConfigFile": "workflow-name.yml"
   }
   ```

### Configuration Fields

- **projectList**: Array of project directory names to update
- **pathToSourceCodeRootDir**: Root directory containing your Artsy code repositories
- **branchName**: Git branch name for changes
- **commitMessage**:  Git commit message (also used as GitHub PR title)
- **prDescription**: GitHub pull request description
- **prReviewer**: GitHub username to review PRs
- **prAssignee**: GitHub username to assign PRs
- **actionConfigFile**: GitHub Action workflow filename (must exist in `duchamp/templates/`)

## Usage

Run the script:
```bash
./run.sh
```

The script will:
1. Validate your configuration
2. For each project in `projectList`:
   - Copy the workflow file from `duchamp/templates/` to `.github/workflows/`
   - Create a new branch
   - Commit changes
   - Create a pull request

## Optional: Auto-merge

To add "Merge On Green" label to PRs:
```bash
MERGE_ON_GREEN=1 ./run.sh
```

## How It Works

The script copies GitHub Action workflow files from a template directory (`duchamp/templates/`) to each project's `.github/workflows/` directory. If the file already exists, it checks for differences and only updates if needed.
