# filesync
Repository for maintaining `filesync`

`filesync` is a harness for running [copier](https://copier.readthedocs.io/en/stable/).

DISCLAIMER: This code repository provided for code sharing purposes and is so provided "as-is". Mezmo, Inc. does not guarantee its functionality. Additionally, some pieces must be supplied in order for builds to be successful, especially base container images for building.

During an `update`, it performs the following actions, in order:

1. Validates its configuration
1. Ensures the `clone-root` directory exists to clone repos into
1. Clones the template provided as a command line argument
1. Loads and validates the template's config
1. Using the template config, determines which repos will have the template applied
1. For each repo, performs the following
    1. Checks the following to see if the repo needs its templated files updated
        1. Does the repo already have an open PR for this version of the template?
            1. If yes, skip this repo
        1. Has the repo been configured to have the template applied to it?
            1. If no, skip this repo
        1. Has the latest version of the template already been applied to the repo?
            1. If yes, skip this repo
    1. Finds and closes any unmerged PRs and their associated branches from older versions of the template
    1. Creates a new update branch (See Branch Names for details)
    1. Runs `copier` to apply the latest version of the template to the update branch
    1. Pushes the changes applied by `copier` to the update branch
    1. Opens a PR from the update branch
1. If `autoclean` is set (it's set by default), removes all repos from the `clone-root` directory

# Branch Names

Branch names are deterministic. They follow this pattern:

```
branch-prefix/repo-template-name/repo-template-sha
```

- `branch-prefix` is configurable, as is the `branch-separator` (though `/`, shown above, is the default)
- `repo-template-name` is the name of the template that was applied to generate the branch
- `repo-template-sha` is the commit hash of the HEAD of the repo template at the time it was applied

Example:
```
```

## Stale Branches

Since `filesync` uses a deterministic branch name, it can find and clean up branches it has opened that were never merged. It can also identify the PRs associated with those branches and close them before deleting the branches.

The exception to this is if the repo's `branch-prefix` or `branch-separator` configuration changes. In that case, `filesync` may create a new branch for the same version of a repo's template or fail to clean up old branches and PRs, because the branch names it's looking for no longer match.

# Commit Messages

Currently, the commit message is controlled by `filesync/commit_template.py`

```
ci: update files from {template}

bringing common files in template up to date
template: {template}
branch: {branch}
commit: {commit}
```

- `template` is the name of the template that was applied
- `branch` is the branch of the template (`main` or `master` typically)
- `commit` is the hash of HEAD of the branch


# Running

## A Template's `Jenkinsfile`

The `Jenkinsfile` in a template repo should be configured to run `filesync`'s `update` command on itself any time changes to it are merged to its `main` / `master` branch.

## Docker

`docker <registry>/<org>/filesync:latest --help`

## Python

Example:
```
python filesync --help
```

Requirements are defined in `requirements.txt` if you want to `pip install -r
requirements.txt` manually. The preferred method of running natively is with
[pipx](https://pypa.github.io/pipx/installation/):

```
git clone git@github.com:mezmo/filesync $WORKDIR/tooling-filesync
cd $WORKDIR/tooling-filesync
pipx install -e .
filesync --help
```

# Configuring

## git

When running inside a container, the following environment variables **must
all** be set:

- `GITHUB_TOKEN` †
- `GIT_AUTHOR_NAME`
- `GIT_AUTHOR_EMAIL`
- `GIT_COMMITTER_NAME`
- `GIT_COMMITTER_EMAIL`

When running natively, if you have a `.gitconfig` with `user.name` and
`user.email` defined, and accessible to Python, only `GITHUB_TOKEN` is
required.

† `GITHUB_TOKEN` is actually configurable in the config yaml you pass at
runtime. The others are core to `git` and can not be changed.

## cli

```
$ filesync --help
Usage: filesync [OPTIONS] TEMPLATE COMMAND [ARGS]...

Options:
  --autoclean / --no-autoclean    remove clones from disk after running
  -r, --clone-root TEXT           path to clone repos
  -d, --dry-run                   don't push changes to cloned repos
  -b, --template-branch TEXT      branch of the template to sync from
  -t, --template-config TEXT      path inside the template repo where its
                                  config is stored
  -e, --token-variable-name TEXT  name of the environment variable storing the
                                  GitHub token
  -l, --log-level TEXT
  --logging-config FILE           path to logging_config.yaml
  --config FILE                   Read configuration from FILE.
  --version                       Show the version and exit.
  --help                          Show this message and exit.

Commands:
  onboard  onboard a repo to be updated by a template
  update   update repos already configured for a template
```

## yaml

`filesync` is configured in multiple places via yaml

### `--config` path

Anything that can be passed to `filesync` via command line options can be configured in a YAML file whose path can be passed via the `--config` flag.

- `autoclean`: (default: `true`) determines whether `filesync` removes the cloned repos from disk
  after running. You probably want this to be `true`, because `filesync` does
  not attempt to change branches or pull before running. Setting to `false`
  should probably only be used for troubleshooting or inspecting changes.
- `clone-root`: (default: `/tmp/filesync_clones`) is the root directory where
  repos will be cloned. You **DO NOT** want this to be `$WORKDIR`, for
  the reasons stated in `autoclean` description.
- `dry-run`: (default: `false`) enable `dry-run` mode for all repos. `dry-run`
  mode is special and has its own configuration sub-section below.
- `template-branch`: (default: `main` or `master` depending on which the template repo uses) which branch of the template should be checked out and run to update desintation repos
- `template-config`: (default: `filesync.yaml`) the path inside the template where the template's filesync config lives (see Template Config)
- `token-variable-name`: (default: `GITHUB_TOKEN`) the name of the environment
  variable where you've stored your Github API token.
- `log-level`: (default: varies) the log level. if dry-run mode is enabled, defaults to `DEBUG`. if sub-command is `update` defaults to `INFO`. if sub-command is `onboard`, defaults to `ERROR`.
- `logging-config`: allows extra control over logging (see Logging Config)

### Template Config

Lives in the template repo (default location `filesync.yaml`). Config options:
- `answers-file`: (default: `.copier-answers.yml`) the path in the destination repo where the config for how this template is applied to it by `copier` is stored
- `autoscan`: (default: `False`) if enabled, `autoscan` clones every repo in the default `org` that isn't a fork, and isn't archived. if that repo has an `answers-file` it is added to the list of repos that will have the template run against them.
- `branch-prefix`: (default: `filesync`) See Branch Names above
- `branch-separator`: (default: `/`) See Branch Names above
- `dry-run`: (default: `False`) run `filesync` in dry-run mode
- `org`: the default GitHub organization if one isn't supplied on the CLI or in the `repos` list for a repo (see Determining Repos and Orgs)
- `repos`: The list of repos this template should be applied to. Each repo can be just the name of the repo, or a map with its own config custom to it, whose keys match the ones in the top level of this config.


### Logging Config

With the exception of `dependency-level`, these settings match [Python standard
config settings for logging](https://docs.python.org/3/howto/logging.html).
These settings are explicitly passed to `logging.basicConfig`, so arbitrary
supported configuration options for the Python standard logging will not be
passed.

- `datefmt` (default: `"%Y-%m-%d %H:%M:%S"`) allows timestamp format to be
  changed independently of the rest of the logging `format`.
- `filename` (default: not set) path to the file to write logs. By leaving this
  unset, logs are printed to the console, which is preferable for running in
  containers and in Jenkins.
- `format` (default: `"%(asctime)s %(levelname)-7s - %(name)s: %(message)s"`)
  The format of the logs.

  Example output:
  ```
  2021-06-18 11:40:56 WARNING - FileSync: DRY RUN MODE ENABLED!
  2021-06-18 11:40:56 INFO    - FileSync: Nothing will be changed inside repos. No branches will be created, no PRs will be opened. Cloning and cleanup will happen as needed.
  2021-06-18 11:40:56 INFO    - FileSync: started!
  ```
- `level` (default: `info`) log level for `filesync`
- `dependency-level` (default: `warn`) log level for imported dependencies.
  Note that these are [manually re-configured in the
  code](https://github.com/mezmo/filesync/blob/main/filesync/filesync.py#L131),
  so if dependencies are added, they may not be impacted by `dependency-level`
  without code changes.

## Determining Repos and Orgs

A repo's org can be defined from `org` at the top level of the template config, or from `org` in its own repo config, but it can also be defined in-line with the repo name:

```
org: a-github-org
repos:
  - some-repo:
      org: a-different-github-org
  - a-third-github-org/some-other-repo
```
