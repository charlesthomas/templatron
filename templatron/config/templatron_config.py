from templatron.config.base_config import BaseConfig


class TemplatronConfig(BaseConfig):
    def __init__(self, *args, **kwargs):
        self.config = dict()
        for key, val in kwargs.items():
            self.config[key] = val
