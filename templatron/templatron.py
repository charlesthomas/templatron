import logging
import os.path
from calendar import monthrange
from datetime import datetime
from os import environ, makedirs
from shutil import rmtree
from sys import exit

from github import Github, GithubException
from sh import ErrorReturnCode, git

from templatron import __version__
from templatron.exceptions import *
from templatron.log_or_print import log_or_print
from templatron.config.templatron_config import TemplatronConfig
from templatron.config.logging_config import LoggingConfig
from templatron.repo.repository import Repository
from templatron.repo.template import Template


class Templatron(object):
    def __init__(self, **kwargs):
        self.config = TemplatronConfig(**kwargs)
        self.template = None
        self.token = environ.get(self.config.token_variable_name)

    def build_repo(self, repo, base_branch=None):
        name, org, kwargs = self.validate_repo(repo)
        gh = self.github.get_organization(org).get_repo(name)
        if base_branch is not None:
            kwargs['base_branch'] = base_branch
        return Repository(name, self.token, gh, self.config.clone_root,
                          self.template, **kwargs)

    def build_repos(self, cache=None):
        self.logger.debug('initializing repos...')
        repos = list()
        if cache is None:
            repo_list = self.fetch_repo_list()
        else:
            repo_list = self.read_repo_list_from_cache(cache)

        if self.template is not None and self.template.config.shard is not None:
            repo_list = self.shard(repo_list)

        for repo in repo_list:
            repos.append(self.build_repo(repo))
        self.logger.debug('repo initialization complete')
        return repos

    def build_template(self, name):
        self.logger.debug(f'initializing template {name}...')
        org, name = self.split_org_and_name(name)
        gh = self.github.get_organization(org).get_repo(name)
        try:
            template = Template(
                name, self.token, gh, self.config.clone_root,
                base_branch=self.config.template_branch,
                dry_run=self.config.dry_run,
                template_config=self.config.template_config,
                operation=self.config.operation,
                interactive=self.config.interactive)
        except TemplatronException as error:
            self.die(error)

        self.logger.debug('template initialization ok')
        return template

    def create_clone_root(self):
        self.logger.debug(f'setting up clone-root: {self.config.clone_root}')
        makedirs(self.config.clone_root, exist_ok=True)

    def die(self, error):
        self.logger.critical(error)
        self.maybe_clean()
        exit(1)

    def fetch_repo_list(self):
        repo_list = list(self.template.config.repos.keys())

        if not self.template.config.autoscan:
            return repo_list

        gh_org = self.github.get_organization(self.template.config.org)
        for repo in gh_org.get_repos():
            if repo.fork:
                self.logger.debug(f"skipping {repo.name}; it's a fork")
                continue
            if repo.archived:
                self.logger.debug(f"skipping {repo.name}; it's archived")
                continue
            if repo.name == self.template.name:
                self.logger.debug(f"skipping {repo.name}; it's the template!")
                continue
            if not self.has_answersfile(repo):
                self.logger.debug(f"skipping {repo.name}; no answersfile")
                continue
            self.logger.debug(f'adding {repo.name} to repo list')
            repo_list.append(repo.name)

        # de-duplicate the list before returning
        return list(set(repo_list))

    def fix(self, repo, branch):
        self.start('fixing')
        try:
            repo = self.build_repo(repo, base_branch=branch)
            repo.fix()
        except UnrecognizableBaseBranchError as error:
            self.die(error)
        except KeyboardInterrupt:
            self.maybe_clean()
            raise
        self.stop()

    def has_answersfile(self, repo):
        # use the github API to try to get the answersfile
        #
        # if the answersfile isn't present, the API will 404
        # detect the 404 exception, skip the repo, and keep scanning
        #
        # if the API throws exception we don't know how to interpret: fail
        #
        # if the API succeeds, it means the answersfile is present, so the
        # template should be synced to the repo
        potential_paths = [self.template.config.answers_file]
        if self.template.config.old_answers_files is not None:
            potential_paths += self.template.config.old_answers_files

        for place in potential_paths:
            try:
                repo.get_contents(place)
                return True
            except GithubException as err:
                if hasattr(err, 'status') and err.status == 404:
                    next
                else:
                    raise
        return False

    def maybe_clean(self):
        if self.config.autoclean and os.path.exists(self.config.clone_root):
            self.logger.info(f'cleaning up {self.config.clone_root}')
            rmtree(self.config.clone_root)

    def maybe_log_dry_run(self):
        if not self.config.dry_run:
            return
        explainer = 'Nothing will be pushed to origin and no PRs will be ' \
                    'opened, but copier will still run and local branches ' \
                    'will still be created. Cloning and cleanup will happen ' \
                    'as needed.'
        log_or_print(self.logger, 'DRY RUN MODE ENABLED!', level='warning')
        log_or_print(self.logger, explainer, level='warning')

    def onboard(self, onboarding_repo):
        self.config.set('onboarding_repo', onboarding_repo)
        self.start(f'onboarding')
        try:
            repo = self.build_repo(onboarding_repo)
            repo.onboard()
        except UnrecognizableBaseBranchError as error:
            self.die(error)
        except KeyboardInterrupt:
            self.maybe_clean()
            raise
        self.stop()

    def read_repo_list_from_cache(self, cache):
        with open(cache) as fin:
            return [i.strip('\n') for i in fin.readlines()]

    def setup_logging(self, command):
        logging_config = LoggingConfig(
            self.config.logging_config, self.config.dry_run,
            operation=self.config.operation, level=self.config.log_level)
        kwargs = dict()
        for option_name in ['filename', 'format', 'datefmt', 'level']:
            option_value = logging_config.get(option_name)
            if option_value is not None:
                if option_name == 'level':
                    option_value = option_value.upper()
                kwargs[option_name] = option_value
        logging.basicConfig(**kwargs)

        # set imported dependency log levels independently of the app
        dep_level = logging_config.get('dependency-level', 'warn').upper()
        for dependency in ['github', 'plumbum', 'sh', 'urllib3']:
            logging.getLogger(dependency).setLevel(dep_level)

        return logging.getLogger('Templatron')

    def shard(self, repo_list):
        self.logger.debug("sharding repo list...")

        now = datetime.now()
        if self.template.config.shard == "weekly":
            mod = 7
            today = now.isoweekday()
        elif self.template.config.shard == "monthly":
            _, mod = monthrange(now.year, now.month)
            today = now.day
        else:
            raise Exception(f"bad shard config: '{self.template.config.shard}'")

        self.logger.debug(f"shard: {self.template.config.shard}")
        self.logger.debug(f"mod: {mod}")
        self.logger.debug(f"today: {today}")

        if today > 0:
            # avoid indexing off-by-one errors
            today = today - 1

        return_list = []
        for i in range(len(repo_list)):
            if i % mod == today:
                return_list.append(repo_list[i])

        return return_list

    def split_org_and_name(self, name):
        parts = name.split('/')
        if len(parts) >= 2:
            org = parts[0]
            name = parts[1]
        else:
            org = self.template.config.org
            if org is None:
                raise MissingRequiredConfigError(
                    "No org was specified in defaults or in the repo name"
                )
            name = parts[0]
        return (org, name)

    def start(self, command):
        self.config.set('operation', command)
        self.logger = self.setup_logging(command)
        self.logger.info(f'Version: {__version__}')
        self.maybe_log_dry_run()
        self.logger.info(f'started {command}')

        self.config.log_config()
        try:
            self.validate_config()
        except TemplatronException as error:
            self.die(error)

        self.create_clone_root()
        self.github = Github(self.token)
        self.template = self.build_template(self.config.template)

    def stop(self):
        self.maybe_clean()
        self.logger.info('finished!')

    def update(self, single_repo=None, cache=None):
        self.start('updating')
        try:
            if single_repo is not None:
                update_repos = [self.build_repo(single_repo)]
            else:
                update_repos = self.build_repos(cache)

            for repo in update_repos:
                try:
                    repo.update()
                except TemplatronException as ex:
                    self.logger.error(
                        f'repo {repo.name} failed with exception: {ex}')
            self.stop()
        except KeyboardInterrupt:
            self.maybe_clean()
            raise

    def validate_config(self):
        self.logger.debug('validating templatron config...')
        if self.token is None:
            raise GitConfigError(
                'No token found! Is token-variable-name '
                f'{self.config.token_variable_name} correct?'
            )
        check_config = False
        required = ['GIT_AUTHOR_EMAIL',
                    'GIT_AUTHOR_NAME',
                    'GIT_COMMITTER_EMAIL',
                    'GIT_COMMITTER_NAME']
        for var in required:
            if environ.get(var) is None:
                check_config = True
        if check_config:
            try:
                git.config('--get', 'user.email')
                git.config('--get', 'user.name')
            except ErrorReturnCode:
                err = 'No git config found! ' \
                      'Set the following variables or see man git-config:\n'
                err += ','.join(required)
                raise GitConfigError(err)
        self.logger.debug('validation ok')

    def validate_repo(self, repo_name):
        kwargs = dict()

        if repo_name in self.template.config.repos.keys():
            # extract the repo's config from the template config file
            data = self.template.config.repos[repo_name]
            for yaml_key, yaml_value in data.items():
                real_key = yaml_key.replace('-', '_')
                kwargs[real_key] = yaml_value

        # figure out what the org is for the repo
        org, name = self.split_org_and_name(repo_name)
        kw_org = kwargs.get('org')
        if kw_org is None:
            kwargs['org'] = org
        elif org is not None and kw_org != org:
            raise AmbiguousOrgConfigError(
                f'repo {name} has more than one org: '
                f'in repo name: {org} in config file: {kw_org}'
            )
            # how does ^ this ^ happen?
            # in the config file, something like
            # repos:
            # - "myorg/myrepo":
            #     org: myOTHERorg

        # use the defaults for any repo config not provided
        for key in ['answers_file', 'branch_prefix', 'branch_separator',
                    'dry_run', 'hooks']:
            kwargs.setdefault(key, self.template.config.get(key))

        # force dry-run if it's enabled globally
        if self.config.dry_run:
            kwargs['dry_run'] = True

        # force interactive if it's enabled globally
        if self.config.interactive:
            kwargs['interactive'] = True

        # this doesn't actually get passed to the Repository object,
        # so pull it out of kwargs
        org = kwargs.pop('org')

        return (name, org, kwargs)
