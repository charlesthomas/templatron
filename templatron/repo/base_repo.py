import logging
import os.path

from sh import ErrorReturnCode, git

from templatron.exceptions import DirtyRepoError, UnrecognizableBaseBranchError


class BaseRepo(object):
    def __init__(self, name, token, github, clone_root, base_branch=None,
                 dry_run=False, interactive=False):

        self.logger = logging.getLogger(f'{self.__class__.__name__}({name})')

        self.name = name
        self.token = token
        self.github = github

        self.clone_root = clone_root
        self.clone_path = os.path.join(clone_root, self.name)

        self.dry_run = dry_run
        self.interactive = interactive

        self._base_branch = base_branch
        self._branches = None

    @property
    def active_branch(self):
        try:
            return self.git_cmd('rev-parse', '--abbrev-ref', 'HEAD').strip()
        except Exception as error:
            raise UnrecognizableBaseBranchError(
                "unable to determine active branch!")

    @property
    def base_branch(self):
        return self._base_branch or self.main

    @property
    def branches(self):
        if self._branches is None:
            self._branches = [b.name for b in self.github.get_branches()]
        return self._branches

    @property
    def clone_url(self):
        return self.github.clone_url.replace(
            'github.com', f'{self.token}@github.com'
        )

    @property
    def head(self):
        return self.github.get_branch(self.base_branch).commit.sha

    @property
    def is_cloned(self):
        return os.path.exists(self.clone_path)

    @property
    def is_dirty(self):
        try:
            result = self.git_cmd('diff', '--quiet')
            return False
        except ErrorReturnCode as err:
            return True

    @property
    def main(self):
        if 'main' in self.branches:
            return 'main'
        if 'master' in self.branches:
            return 'master'
        raise UnrecognizableBaseBranchError("unable to determine base branch!")

    def clone(self):
        if not self.is_cloned:
            self.logger.debug(f'cloning {self.name} to {self.clone_path}...')
            # it's fine to do shallow clones (--depth 1), as long as we change
            # branches correctly
            self.git_cmd('clone', '--depth', '1',
                         self.clone_url, self.clone_path)
        if self.is_dirty:
            raise DirtyRepoError(
                f"repo {self.name} is dirty! can't proceed")
        self.maybe_switch_branch()
        self.logger.debug(f'cloning {self.name} complete')

    def git_cmd(self, cmd, *args):
        if cmd == 'clone':
            # clone is special because _cwd doesn't exist yet
            return git(cmd, *args)
        return git(cmd, *args, _cwd=self.clone_path)

    def maybe_switch_branch(self):
        if self.active_branch == self.base_branch:
            return
        self.logger.info(
            f'switching from {self.active_branch} to {self.base_branch}')
        self.git_cmd('remote', 'set-branches', 'origin', self.base_branch)
        self.git_cmd('fetch', '--depth', '1', 'origin', self.base_branch)
        self.git_cmd('checkout', self.base_branch)
