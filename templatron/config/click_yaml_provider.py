from templatron.config.base_config import BaseConfig


def click_yaml_provider(file_path, cmd_name):
    return ClickYamlProvider(file_path).config


class ClickYamlProvider(BaseConfig):
    SAFE_DEFAULTS = dict()
