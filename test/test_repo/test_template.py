"""
Unit tests for templatron/repo/template.py
"""
# pylint: disable=protected-access

from unittest import TestCase
from unittest.mock import MagicMock, patch

from templatron.exceptions import (
    MissingRequiredConfigError,
    TemplateConfigMissingError,
)
from templatron.repo.template import Template


class TestTemplate(TestCase):
    """
    Tests for templatron.repo.template:Template
    """

    def setUp(self):
        with patch("templatron.repo.template.BaseRepo.clone"):
            with patch("templatron.repo.template.Template.load_template_config"):
                self.template = Template(
                    name="test_template",
                    token="fake_token",
                    github="fake_github",
                    clone_root="fake_root",
                )

    @patch("templatron.repo.template.os.path")
    def test_load_template_config_path_does_not_exist(self, mock_path):
        """
        Test Template.load_template_config() where the given config path
        doesn't exist
        """

        mock_path.exists.return_value = False
        with self.assertRaises(TemplateConfigMissingError):
            self.template.load_template_config("fake_config")

    @patch("templatron.repo.template.TemplateConfig")
    @patch("templatron.repo.template.BaseRepo.maybe_switch_branch")
    @patch("templatron.repo.template.Template.validate_template_config")
    @patch("templatron.repo.template.os.path")
    def test_load_template_config_template_branch_is_not_none(
        self,
        mock_path,
        mock_validate,
        mock_maybe,
        mock_config,
    ):
        """
        Test Template.load_template_config() where the given template_branch
        is not None
        """

        mock_path.exists.return_value = True
        mock_config().template_branch = "fake_branch"
        self.template.load_template_config("fake_config")
        mock_validate.assert_called_with()
        mock_maybe.assert_called_with()
        self.assertEqual(self.template._base_branch, "fake_branch")

    @patch("templatron.repo.template.TemplateConfig")
    @patch("templatron.repo.template.BaseRepo.maybe_switch_branch")
    @patch("templatron.repo.template.Template.validate_template_config")
    @patch("templatron.repo.template.os.path")
    def test_load_template_config_template_branch_is_none(
        self,
        mock_path,
        mock_validate,
        mock_maybe,
        mock_config,
    ):
        """
        Test Template.load_template_config() where the given template_branch
        is None
        """

        mock_path.exists.return_value = True
        mock_config().template_branch = None
        self.template._base_branch = "fake_branch"
        self.template.load_template_config("fake_config")
        mock_validate.assert_called_with()
        mock_maybe.assert_called_with()
        self.assertEqual(self.template._base_branch, "fake_branch")

    def test_validate_template_config_no_org(self):
        """
        Test Template.validate_template_config() where org is not defined in
        template config.
        """

        self.template.config = MagicMock()
        self.template.config.org = None
        with self.assertRaises(MissingRequiredConfigError):
            self.template.validate_template_config()

    def test_validate_template_config_none_repos(self):
        """
        Test Template.validate_template_config() where operation is "updating",
        autoscan is not enabled, and Template.config.repos is not defined.
        """

        self.template.config = MagicMock()
        self.template.config.org = "Fake Organization"
        self.template.config.autoscan = False
        self.template.config.repos = None
        self.template.operation = "updating"
        with self.assertRaises(MissingRequiredConfigError):
            self.template.validate_template_config()

    def test_validate_template_config_zero_repos(self):
        """
        Test Template.validate_template_config() where operation is "updating",
        autoscan is not enabled, and Template.config.repos is not defined.
        """

        self.template.config = MagicMock()
        self.template.config.org = "Fake Organization"
        self.template.config.autoscan = False
        self.template.config.repos = []
        self.template.operation = "updating"
        with self.assertRaises(MissingRequiredConfigError):
            self.template.validate_template_config()
