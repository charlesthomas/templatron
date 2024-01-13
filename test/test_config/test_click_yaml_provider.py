"""
Test functionality of config/click_yaml_provider.py
"""

from unittest import TestCase
from unittest.mock import patch

from filesync.config.click_yaml_provider import click_yaml_provider


class TestClickYamlProviderMethod(TestCase):
    """
    Test click_yaml_provider()
    """

    @staticmethod
    @patch("filesync.config.click_yaml_provider.ClickYamlProvider")
    def test_click_yaml_provider_valid(mock_provider):
        """
        Test click_yaml_provider() with valid arguments
        """

        click_yaml_provider("/fake/path", "fake_cmd")
        mock_provider.assert_called_with("/fake/path")
