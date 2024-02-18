from pprint import pformat

from templatron.config.base_config import BaseConfig
from templatron.exceptions import UnrecognizedRepoConfigError


class TemplateConfig(BaseConfig):
    SAFE_DEFAULTS = {
        "answers_file": ".copier-answers.yml",
        "autoscan": False,
        "branch_prefix": "templatron",
        "branch_separator": "-",
        "repos": [],
        "hooks": {},
    }

    def __init__(self, config_path):
        super().__init__(config_path)

        self.repos = self.configure_repos()

    def configure_repos(self):
        # because yaml, each repo in the config file could either be a string
        # or a dict; just make them all dicts now
        repos = dict()
        for repo in self.config.get("repos", []):
            if type(repo) == str:
                name = repo
                repos[name] = dict()
            elif type(repo) == dict:
                keys = list(repo.keys())
                if len(keys) != 1:
                    raise UnrecognizedRepoConfigError(
                        "Something is misconfigured! "
                        "This should have exactly one key."
                        f"\n{pformat(repo)}"
                    )
                name = keys[0]
                repos[name] = repo[name]
            else:
                raise UnrecognizedRepoConfigError(
                    "Something is misconfigured! "
                    "Unrecognized repo config type."
                    f"\n{pformat(repo)}"
                )
        return repos
