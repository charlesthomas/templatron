#!/usr/bin/env python
import os.path
from tempfile import gettempdir

import click
import click_config_file

from templatron import __version__
from templatron.templatron import Templatron
from templatron.config.click_yaml_provider import click_yaml_provider


DEFAULT_CLONE_ROOT = os.path.join(gettempdir(), 'templatron_clones')


@click.group()
@click.pass_context
@click.argument('template')
@click.option('--autoclean/--no-autoclean', default=True,
              help='remove clones from disk after running')
@click.option('--clone-root', '-r', default=DEFAULT_CLONE_ROOT,
              help='path to clone repos')
@click.option('--dry-run', '-d', default=False, is_flag=True,
              help="don't push changes to cloned repos")
@click.option('--interactive', '-i', default=False, is_flag=True,
              help='run in interactive mode to be asked onboarding questions')
@click.option('--log-level', '-l')
@click.option('--logging-config',
              type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help='path to logging_config.yaml')
@click.option('--template-branch', '-b',
              help='branch of the template to sync from')
@click.option('--template-config', '-t', default='templatron.yaml',
              help='path inside the template repo where its config is stored')
@click.option('--token-variable-name', '-e', default='GITHUB_TOKEN',
              help='name of the environment variable storing the GitHub token')
@click_config_file.configuration_option(provider=click_yaml_provider,
                                        implicit=False)
@click.version_option(version=__version__)
def main(ctx, template, autoclean, clone_root, dry_run, template_branch,
         template_config, token_variable_name, log_level, logging_config,
         interactive):

    ctx.obj = Templatron(template=template, autoclean=autoclean,
                       clone_root=clone_root, dry_run=dry_run,
                       template_branch=template_branch,
                       template_config=template_config,
                       token_variable_name=token_variable_name,
                       log_level=log_level, logging_config=logging_config,
                       interactive=interactive)


@main.command(help='update repos already configured for a template')
@click.pass_context
@click.option('--single-repo', '-1',
              help='update this repo only; bypass repo list / scanning')
@click.option('--cache', '-c',
              help="don't query the GitHub API; use a cached list of repos")
def update(ctx, single_repo, cache):
    templatron = ctx.obj
    templatron.update(single_repo, cache)


@main.command(help='onboard a repo to be updated by a template')
@click.pass_context
@click.argument('onboarding_repo')
def onboard(ctx, onboarding_repo):
    templatron = ctx.obj
    templatron.onboard(onboarding_repo)


@main.command(help='fix an existing template PR')
@click.pass_context
@click.argument('repo')
@click.argument('existing_branch')
def fix(ctx, repo, existing_branch):
    templatron = ctx.obj
    templatron.fix(repo, existing_branch)


if __name__ == '__main__':
    main()
