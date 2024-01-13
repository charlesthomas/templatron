"""
Test config/logging_config.py
"""

from unittest import TestCase
from unittest.mock import patch

from templatron.config.logging_config import LoggingConfig


class TestLoggingConfig(TestCase):
    """
    Test class for LoggingConfig class
    """

    def setUp(self):
        with patch(
            "templatron.config.logging_config.BaseConfig.load_config"
        ) as mock_load:
            mock_load.return_value = {}
            self.log_class = LoggingConfig("/fake/config/path")

    def test_get_level_level_is_set(self):
        """
        Test LoggingConfig.get_level() with the level parameter set
        """

        result = self.log_class.get_level(
            dry_run=True,
            operation="not updating",
            level="constantinople",
        )
        self.assertEqual(result, "constantinople")

    def test_get_level_dry_run_is_true(self):
        """
        Test LoggingConfig.get_level() with the dry_run parameter is True
        """

        result = self.log_class.get_level(
            dry_run=True,
            operation="not updating",
            level=None,
        )
        self.assertEqual(result, "debug")

    def test_get_level_operation_is_not_updating(self):
        """
        Test LoggingConfig.get_level() with the operation parameter is not
        "updating"
        """

        result = self.log_class.get_level(
            dry_run=False,
            operation="not updating",
            level=None,
        )
        self.assertEqual(result, "error")

    def test_get_level_operation_is_updating(self):
        """
        Test LoggingConfig.get_level() with the operation parameter is
        "updating"
        """

        self.log_class.config = {}
        result = self.log_class.get_level(
            dry_run=False,
            operation="updating",
            level=None,
        )
        self.assertEqual(result, "info")
