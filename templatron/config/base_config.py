import logging
from pprint import pformat

from yaml import safe_load


class BaseConfig(object):
    def __init__(self, config_path):
        if config_path is None:
            self.config = dict()
        else:
            self.config_path = config_path
            self.config = self.load_config(self.config_path)

        for key, val in self.SAFE_DEFAULTS.items():
            self.config.setdefault(key, val)

        self.logger = None

    def __getattr__(self, key):
        # allow config to be read using config.some_setting,
        # in addition to config['some_setting'] and config.get('some_setting')
        return self.get(key)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, val):
        self.config[key] = val

    def load_config(self, config_path):
        config = dict()
        with open(config_path) as fin:
            from_yaml = safe_load(fin.read())
            if not from_yaml:
                return {}
            for yaml_key, val in from_yaml.items():
                key = yaml_key.replace("-", "_")
                if type(val) == str and val == "":
                    # make our lives easier so we don't have to always check
                    # if value is None or value == '':
                    # everywhere we check the config
                    val = None
                config[key] = val
        return config

    def log_config(self):
        if self.logger is None:
            self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"config path loaded: {self.config_path}")
        filtered = {k: v for (k, v) in self.config.items() if v is not None}
        self.logger.info(f"with config:\n{pformat(filtered)}")
