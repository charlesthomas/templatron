from filesync.config.base_config import BaseConfig


class LoggingConfig(BaseConfig):
    SAFE_DEFAULTS = {
        'format': '%(asctime)s %(levelname)-8s - %(name)s: %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'level': 'info',
        'dependency_level': 'warn',
    }

    def __init__(self, config_path, dry_run=False, operation='updating',
                 level=None):
        super().__init__(config_path)
        self.config['level'] = self.get_level(dry_run, operation, level)

    def get_level(self, dry_run, operation, level):
        if level is not None:
            return level
        if dry_run:
            return 'debug'
        if operation != 'updating':
            return 'error'
        return self.config.get('level', self.SAFE_DEFAULTS.get('level'))
