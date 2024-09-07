# 🤖 templatron

`templatron` is a harness for running [copier](https://copier.readthedocs.io/en/stable/).

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
branchPrefix-repoTemplateName-repoTemplateShortSha
```

- `branch-prefix` is configurable, as is the `branch-separator` (though `-`, shown above, is the default)
- `repo-template-name` is the name of the template that was applied to generate the branch
- `repo-template-sha` is the short commit hash of the HEAD of the repo template at the time it was applied

## Stale Branches

Since `templatron` uses a deterministic branch name, it can find and clean up branches it has opened that were never merged. It can also identify the PRs associated with those branches and close them before deleting the branches.

The exception to this is if the repo's `branch-prefix` or `branch-separator` configuration changes. In that case, `templatron` may create a new branch for the same version of a repo's template or fail to clean up old branches and PRs, because the branch names it's looking for no longer match.

# Commit Messages

Currently, the commit message is controlled by `templatron/commit_template.py`

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

This repo uses [`poetry`](https://python-poetry.org/), and defines user (normal) and dev dependencies.

To install them all:

```
poetry install
poetry run templatron --help
```

To install only the user dependencies (and not the dev dependencies):

```
poetry install --without dev
poetry run templatron --help
```

If you don't want to bother with poetry, you can use [`pipx`](https://pipx.pypa.io/latest/installation/) instead:

```
pipx install .
templatron --help
```

🤖 templatron also installs as `tt`:

```
poetry install
tt --help
```

or

```
pipx install .
tt --help
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
$ templatron --help
Usage: templatron [OPTIONS] TEMPLATE COMMAND [ARGS]...

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

`templatron` is configured in multiple places via yaml

### `--config` path

Anything that can be passed to `templatron` via command line options can be configured in a YAML file whose path can be passed via the `--config` flag.

- `autoclean`: (default: `true`) determines whether `templatron` removes the cloned repos from disk
  after running. You probably want this to be `true`, because `templatron` does
  not attempt to change branches or pull before running. Setting to `false`
  should probably only be used for troubleshooting or inspecting changes.
- `clone-root`: (default: `/tmp/templatron_clones`) is the root directory where
  repos will be cloned. You **DO NOT** want this to be `$WORKDIR`, for
  the reasons stated in `autoclean` description.
- `dry-run`: (default: `false`) enable `dry-run` mode for all repos. `dry-run`
  mode is special and has its own configuration sub-section below.
- `template-branch`: (default: `main` or `master` depending on which the template repo uses) which branch of the template should be checked out and run to update desintation repos
- `template-config`: (default: `templatron.yaml`) the path inside the template where the template's templatron config lives (see Template Config)
- `token-variable-name`: (default: `GITHUB_TOKEN`) the name of the environment
  variable where you've stored your Github API token.
- `log-level`: (default: varies) the log level. if dry-run mode is enabled, defaults to `DEBUG`. if sub-command is `update` defaults to `INFO`. if sub-command is `onboard`, defaults to `ERROR`.
- `logging-config`: allows extra control over logging (see Logging Config)

### Template Config

Lives in the template repo (default location `templatron.yaml`). Config options:
- `answers-file`: (default: `.copier-answers.yml`) the path in the destination repo where the config for how this template is applied to it by `copier` is stored
- `autoscan`: (default: `False`) if enabled, `autoscan` clones every repo in the default `org` that isn't a fork, and isn't archived. if that repo has an `answers-file` it is added to the list of repos that will have the template run against them.
- `branch-prefix`: (default: `templatron`) See Branch Names above
- `branch-separator`: (default: `/`) See Branch Names above
- `dry-run`: (default: `False`) run `templatron` in dry-run mode
- `hooks`: hooks can run scripts at certain points during the onboarding and / or updating operations. see [hooks](#hooks) for more details
- `old-answers-files`: this is a `list` of answersfiles that _used to be, but are no longer used_. when running autoscan, `tempaltron` will run against a repo if the current answers file is missing, but one of the `old-answers-files` is present. You'll need to include a `pre-copier` hook to `git mv` the old answers file to the current location, or else your answers **WILL NOT** be loaded during the update.
- `org`: the default GitHub organization or user if one isn't supplied on the CLI or in the `repos` list for a repo (see Determining Repos and Orgs). `templatron` assumes all repos belong to a GitHub organization (rather than a user) when making API calls. If GitHub's API returns a `404` when making a `get_organization` call, `templatron` will automatically retry with `get_user` instead.
- `repos`: The list of repos this template should be applied to. Each repo can be just the name of the repo, or a map with its own config custom to it, whose keys match the ones in the top level of this config.
- `shard`: Shard setting can be `weekly` or `monthly`. Sharding can be used to reduce the number of repos that will be updated when running `templatron update`. The expectation is that a `shard`-ed config is running daily via CI, and that either 1/7th or 1/30th of the repos should be updated per day.

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
  2021-06-18 11:40:56 WARNING - Templatron: DRY RUN MODE ENABLED!
  2021-06-18 11:40:56 INFO    - Templatron: Nothing will be changed inside repos. No branches will be created, no PRs will be opened. Cloning and cleanup will happen as needed.
  2021-06-18 11:40:56 INFO    - Templatron: started!
  ```
- `level` (default: `info`) log level for `templatron`
- `dependency-level` (default: `warn`) log level for imported dependencies.
  Note that these are manually re-configured in the code, so if dependencies are
  added, they may not be impacted by `dependency-level` without code changes.

## Determining Repos and Orgs

A repo's org can be defined from `org` at the top level of the template config, or from `org` in its own repo config, but it can also be defined in-line with the repo name:

```
org: a-github-org
repos:
  - some-repo:
      org: a-different-github-org
  - a-third-github-org/some-other-repo
```

## Hooks

There are 6 different hooks:

1. `pre-clone`: runs immediately before a repo is cloned
1. `post-clone`: runs immediately after a repo is cloned
1. `pre-copier`: runs immediately before `copier` runs to apply the template
1. `post-copier`: runs immediately after `copier` runs to apply the template
1. `pre-push`: runs imediately before the git commit is pushed to origin
1. `post-push`: runs immediately after the git commit ish pushed to origin

Hooks shell out to run whatever the value of the key is.

Example:

```yaml
hooks:
  pre-copier-hook: my-hook.sh
```

With the above hook config, `templatron` will run `my-hook.sh` and then run `copier` to apply the template to the repo.

It is expected that hook scripts can receive these four arguments, in order:
1. operation: either `onboard` or `update`. can be used to only run a hook on updates or only run a hook when onboarding a new repo
1. clone root: the location `templatron` is cloning repos to. for hook scripts to be able to access the correct files on disk
1. repo name: the name of the repo the hook is running against. can be used along with clone root to access files inside the repo.
1. answers file: the path of the answers file relative to the root of the repo.

Example:

`my-hook.sh onboard /tmp/templatron-clones destination-repo src/answers.yaml`

in this example, the full path to the answers file templatron cloned to disk and will read from is `/tmp/templatron-clones/destination-repo/src/answers.yaml`.
