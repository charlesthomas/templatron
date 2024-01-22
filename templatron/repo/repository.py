import logging
import os.path
import subprocess

import yaml
from copier import run_copy, run_update

from templatron.commit_template import commit_template
from templatron.exceptions import HookFailure
from templatron.log_or_print import log_or_print
from templatron.repo.base_repo import BaseRepo


def string_representer(dumper, data):
    # this custom function will be used by yaml.dump
    # to change multi-line strings from something like this:
    # key: "this\nis\nfour\nlines"
    # to something like this:
    # key: |
    #   this
    #   is
    #   four
    #   lines
    style = None
    if '\n' in data:
        style = '|'
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)


class Repository(BaseRepo):
    def __init__(
        self, name, token, github, clone_root, template,
        base_branch=None, dry_run=False,
        answers_file='.copier-answers.yml',
        branch_prefix='templatron',
        branch_separator='/',
        interactive=False,
        hooks=None):

        super().__init__(
            name, token, github, clone_root, base_branch, dry_run, interactive
        )
        self.template = template
        self.answers_file = answers_file
        self.branch_prefix = branch_prefix
        self.branch_separator = branch_separator
        self.hooks = hooks or {}

        self.operation = None

        self.answers_file_path = os.path.join(
            self.clone_path, self.answers_file)

    @property
    def commit_message(self):
        return commit_template.format(
            operation=self.operation,
            template=self.template.name,
            branch=self.template.base_branch,
            commit=self.template.head
        )

    @property
    def fixing(self):
        return self.operation == 'fixing'

    @property
    def has_update_branch(self):
        return self.update_branch_name in self.branches

    @property
    def template_version(self):
        with open(self.answers_file_path) as fin:
            answers = yaml.safe_load(fin.read())
        return answers.get(
            '_template_version',
            '_template_version missing, force update'
        )

    @property
    def onboarding(self):
        return self.operation == 'onboarding'

    @property
    def needs_update(self):
        if self.has_update_branch:
            self.logger.debug(
                f'SKIP: update branch exists: {self.update_branch_name}')
            return False
        if self.template.head.startswith(self.template_version):
            self.logger.info(
                'SKIP: template version matches template head: '
                f'{self.template_version}')
            return False
        return True

    @property
    def update_branch_name(self):
        if self.fixing:
            return self.base_branch

        return self.branch_separator.join([
            self.branch_prefix,
            self.template.name,
            self.template.head
        ])

    @property
    def updating(self):
        return self.operation == 'updating'

    def clean_stale_branches(self):
        # find stale branches, close the associated PRs, delete the branches
        start = self.branch_separator.join([
            self.branch_prefix, self.template.name
        ])
        self.logger.debug(f'clean old branches matching prefix {start}...')
        for branch in self.github.get_branches():
            if branch.name.startswith(start):
                for pr in branch.commit.get_pulls():
                    self.close_pr(pr)
                self.delete_branch(branch)
        self.logger.debug('clean complete')

    def close_pr(self, pr):
        self.logger.debug(f'close PR #{pr.number}: {pr.title}')
        if self.dry_run:
            return
        pr.edit(state='closed')

    def confirm_changes(self):
        # if the only thing that copier changed is the answers file,
        # don't bother opening a PR
        changes = self.git_cmd('status', '--short').split('\n')[:-1]
        # ^ [:-1] drops the last line of output b/c it's always a blank line
        if len(changes) == 0:
            self.logger.info('no changes detected')
            return False
        if len(changes) == 1 and self.answers_file in changes[0]:
            self.logger.info('only the answers file changed; nothing to do.')
            return False
        return True

    def delete_branch(self, branch):
        self.logger.debug(f'delete branch {branch.name}')
        if self.dry_run:
            return
        self.git_cmd('push', 'origin', '--delete', branch.name)

    def fix(self):
        self.update(operation='fixing')

    def post_clone_hook(self):
        self.run_hook('post-clone')

    def post_copier_hook(self):
        self.run_hook('post-copier')

    def post_push_hook(self):
        self.run_hook('post-push')

    def pre_clone_hook(self):
        self.run_hook('pre-clone')

    def pre_copier_hook(self):
        self.run_hook('pre-copier')

    def pre_push_hook(self):
        self.run_hook('pre-push')

    def onboard(self):
        self.update(operation='onboarding')

    def open_pull_request(self):
        if self.fixing:
            # pr should already exist; just find it
            pr = self.github.get_branch(self.base_branch).commit.get_pulls()[0]
        else:
            parts = self.commit_message.split('\n')
            title = parts[0]
            body = '\n'.join(parts[2:])
            # parts[1] is a blank line
            head = self.update_branch_name
            base = self.base_branch

            self.logger.debug(f'open PR to merge {head} into {base}')
            if self.dry_run:
                return
            pr = self.github.create_pull(
                title=title, body=body, head=head, base=base)
        log_or_print(self.logger, pr.html_url)

    def push_changes(self):
        self.logger.debug(f'push changes with message\n{self.commit_message}')
        if self.dry_run:
            return
        self.git_cmd('push', 'origin', self.update_branch_name)
        self.git_cmd(
            'remote', 'set-branches', 'origin',
            self.update_branch_name
        )
        self.git_cmd(
            'fetch', '--depth', '1', 'origin',
            self.update_branch_name
        )
        self.git_cmd(
            'branch', '--set-upstream-to',
            f'origin/{self.update_branch_name}'
        )
        self.git_cmd('add', '-A')
        self.git_cmd('commit', '-m', self.commit_message)
        self.git_cmd('push')

    def run_copier(self):
        if self.interactive:
            quiet = False
        else:
            quiet = not self.dry_run

        self.template.clone()
        # this is a no-op if it's already been cloned

        if self.operation == 'updating':
            self.logger.debug(f'''running copier to apply template...

run_update({self.template.clone_path}, {self.clone_path},
answers_file={self.answers_file}, overwrite=True, quiet={quiet},
vcs_ref={self.template.vcs_ref})''')

            run_update(
                self.clone_path, answers_file=self.answers_file,
                defaults=True, overwrite=True, quiet=quiet,
                src_path=self.template.clone_path,
                vcs_ref=self.template.vcs_ref
            )

        else: # onboarding or fixing
            self.logger.debug(f'''running copier to apply template...

run_copy({self.template.clone_path}, {self.clone_path},
answers_file={self.answers_file}, quiet={quiet},
vcs_ref={self.template.vcs_ref})''')

            run_copy(
                self.template.clone_path, self.clone_path,
                answers_file=self.answers_file,
                quiet=quiet, vcs_ref=self.template.vcs_ref
            )

        self.logger.debug('copier done')

    def run_hook(self, hook_name):
        hook = self.hooks.get(hook_name)
        if hook is None:
            return
        args = [os.path.join(self.template.clone_path, hook),
                self.operation, self.clone_root, self.name, self.answers_file]
        self.logger.info(
            f'running {hook_name} hook: {hook} {" ".join(args[1:])}')
        res = subprocess.run(args, capture_output=True)
        if res.returncode != 0:
            raise HookFailure(
                f'{hook_name} hook {hook} failed with exit code '
                f'{res.returncode} stderr: "'
                f'{res.stderr.decode("UTF-8").strip()}"')

    def switch_to_update_branch(self):
        if self.fixing:
            # we're already on the update branch
            return

        self.logger.debug(f'switch to update branch {self.update_branch_name}')
        self.git_cmd('checkout', '-b', self.update_branch_name)

    def update(self, operation='updating'):
        self.operation = operation

        self.logger.info(f'{operation} {self.name}...')

        self.pre_clone_hook()
        self.clone(shallow=True)
        self.post_clone_hook()

        self.switch_to_update_branch()
        self.pre_copier_hook()
        if self.updating and not self.needs_update:
            return
        self.run_copier()
        self.post_copier_hook()
        if not self.confirm_changes():
            return

        self.pre_push_hook()
        if not self.fixing:
            self.clean_stale_branches()
        self.push_changes()
        self.open_pull_request()
        self.post_push_hook()

        self.logger.info(f'{self.name} complete')
