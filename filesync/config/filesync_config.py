from filesync.config.base_config import BaseConfig


class FilesyncConfig(BaseConfig):
    def __init__(self, *args, **kwargs):
        self.config = dict()
        for key, val in kwargs.items():
            self.config[key] = val
