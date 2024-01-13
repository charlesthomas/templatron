"""
Test functions in cli.py
"""

from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from templatron.cli import main


class TestUpdate(TestCase):
    """
    Test update() method

    This is a wrapper method, so not much testing is needed
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @patch("templatron.cli.Templatron")
    def test_update_valid(self, mock_templatron):
        """
        Test update() with no arguments
        """

        self.runner.invoke(main, ["template", "update"])
        mock_templatron().update.assert_called()

    @patch("templatron.cli.Templatron")
    def test_update_one_repo(self, mock_templatron):
        """
        Test update() with no arguments
        """

        self.runner.invoke(main, ["template", "update", "-1", "single_repo"])
        mock_templatron().update.assert_called_with("single_repo", None)


class TestOnboard(TestCase):
    """
    Test onboard() method

    This is a wrapper method, so not much testing is needed
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @patch("templatron.cli.Templatron")
    def test_onboard_valid(self, mock_templatron):
        """
        Test onboard() with valid arguments
        """

        self.runner.invoke(main, ["template", "onboard", "onboarding_repo"])
        mock_templatron().onboard.assert_called_with("onboarding_repo")

    @patch("templatron.cli.Templatron")
    def test_onboard_no_repo(self, mock_templatron):
        """
        Test onboard() with no arguments
        """

        res = self.runner.invoke(main, ["template", "onboard"])
        self.assertEqual(res.exit_code, 2)
        mock_templatron().onboard.assert_not_called()


class TestFix(TestCase):
    """
    Test Fix() method

    This is a wrapper method, so not much testing is needed
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @patch("templatron.cli.Templatron")
    def test_fix_valid(self, mock_templatron):
        """
        Test fix() with valid arguments
        """

        self.runner.invoke(main, ["template", "fix", "repo", "existing_branch"])
        mock_templatron().fix.assert_called_with("repo", "existing_branch")

    @patch("templatron.cli.Templatron")
    def test_fix_no_args(self, mock_templatron):
        """
        Test update() with no args
        """

        res = self.runner.invoke(main, ["template", "fix"])
        self.assertEqual(res.exit_code, 2)
        mock_templatron().fix.assert_not_called()
