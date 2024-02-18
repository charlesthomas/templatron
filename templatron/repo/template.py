import os.path

from templatron.config.template_config import TemplateConfig
from templatron.exceptions import MissingRequiredConfigError, TemplateConfigMissingError
from templatron.repo.base_repo import BaseRepo


class Template(BaseRepo):
    def __init__(
        self,
        name,
        token,
        github,
        clone_root,
        base_branch=None,
        dry_run=False,
        template_config="templatron.yaml",
        operation="updating",
        interactive=False,
    ):

        super().__init__(
            name, token, github, clone_root, base_branch, dry_run, interactive
        )

        self.operation = operation
        self.clone()
        self.vcs_ref = None
        self.load_template_config(template_config)

    def load_template_config(self, template_config):
        config_path = os.path.join(self.clone_path, template_config)
        if not os.path.exists(config_path):
            raise TemplateConfigMissingError(
                f"{template_config} not found in {self.name}!"
            )
        self.config = TemplateConfig(config_path)
        self.validate_template_config()
        # we have to update _base_branch again here, because it's in the config
        # file in its own repo, so we don't know the value until after cloning
        if self.config.template_branch is not None:
            self._base_branch = self.config.template_branch
        self.vcs_ref = self.base_branch
        self.config.log_config()
        self.maybe_switch_branch()

    def validate_template_config(self):
        self.logger.debug("validating template config...")
        if self.config.org is None:
            raise MissingRequiredConfigError("org is required!")
        if (
            self.operation == "updating"
            and not self.config.autoscan
            and (self.config.repos is None or len(self.config.repos) == 0)
        ):
            raise MissingRequiredConfigError(
                "repo list is empty and autoscan is disabled! nothing to do!"
            )
