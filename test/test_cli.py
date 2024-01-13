"""
Test functions in cli.py
"""

from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from filesync.cli import main


class TestUpdate(TestCase):
    """
    Test update() method

    This is a wrapper method, so not much testing is needed
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @patch("filesync.cli.FileSync")
    def test_update_valid(self, mock_filesync):
        """
        Test update() with no arguments
        """

        self.runner.invoke(main, ["template", "update"])
        mock_filesync().update.assert_called()

    @patch("filesync.cli.FileSync")
    def test_update_one_repo(self, mock_filesync):
        """
        Test update() with no arguments
        """

        self.runner.invoke(main, ["template", "update", "-1", "single_repo"])
        mock_filesync().update.assert_called_with("single_repo", None)


class TestOnboard(TestCase):
    """
    Test onboard() method

    This is a wrapper method, so not much testing is needed
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @patch("filesync.cli.FileSync")
    def test_onboard_valid(self, mock_filesync):
        """
        Test onboard() with valid arguments
        """

        self.runner.invoke(main, ["template", "onboard", "onboarding_repo"])
        mock_filesync().onboard.assert_called_with("onboarding_repo")

    @patch("filesync.cli.FileSync")
    def test_onboard_no_repo(self, mock_filesync):
        """
        Test onboard() with no arguments
        """

        res = self.runner.invoke(main, ["template", "onboard"])
        self.assertEqual(res.exit_code, 2)
        mock_filesync().onboard.assert_not_called()


class TestFix(TestCase):
    """
    Test Fix() method

    This is a wrapper method, so not much testing is needed
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @patch("filesync.cli.FileSync")
    def test_fix_valid(self, mock_filesync):
        """
        Test fix() with valid arguments
        """

        self.runner.invoke(main, ["template", "fix", "repo", "existing_branch"])
        mock_filesync().fix.assert_called_with("repo", "existing_branch")

    @patch("filesync.cli.FileSync")
    def test_fix_no_args(self, mock_filesync):
        """
        Test update() with no args
        """

        res = self.runner.invoke(main, ["template", "fix"])
        self.assertEqual(res.exit_code, 2)
        mock_filesync().fix.assert_not_called()
