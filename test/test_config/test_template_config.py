"""
Test config/template_config.py
"""

from unittest import TestCase
from unittest.mock import patch

from templatron.config.template_config import TemplateConfig
from templatron.exceptions import UnrecognizedRepoConfigError


class TestTemplateConfig(TestCase):
    """
    Test class for TemplateConfig class
    """

    def setUp(self):
        with patch(
            "templatron.config.template_config.BaseConfig.load_config"
        ) as mock_load:
            mock_load.return_value = {}
            self.template_class = TemplateConfig("/fake/config/path")

    def test_configure_repos_with_repo_name(self):
        """
        Test TemplateConfig.configure_repos() given the name of a repo
        """

        self.template_class.config["repos"] = ["repo_name"]
        result = self.template_class.configure_repos()
        self.assertEqual(result, {"repo_name": {}})

    def test_configure_repos_with_repo_dict_valid(self):
        """
        Test TemplateConfig.configure_repos() given a valid repo as a dict
        """

        fake_repo = {"repo_name": {"some": "data", "other": "stuff"}}
        self.template_class.config["repos"] = [fake_repo]
        result = self.template_class.configure_repos()
        self.assertEqual(result, fake_repo)

    def test_configure_repos_with_repo_dict_too_many_keys(self):
        """
        Test TemplateConfig.configure_repos() given a dict with too many keys
        """

        fake_repo = {
            "repo_name": {
                "some": "data",
                "other": "stuff",
            },
            "bad_apple": 1,
        }
        self.template_class.config["repos"] = [fake_repo]
        with self.assertRaises(UnrecognizedRepoConfigError):
            result = self.template_class.configure_repos()
            self.assertEqual(result, None)

    def test_configure_repos_with_invalid_repo_type(self):
        """
        Test TemplateConfig.configure_repos() given a repo that isn't a string
        or dict
        """

        fake_repo = object()
        self.template_class.config["repos"] = [fake_repo]
        with self.assertRaises(UnrecognizedRepoConfigError):
            result = self.template_class.configure_repos()
            self.assertEqual(result, None)
