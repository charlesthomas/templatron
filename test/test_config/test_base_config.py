"""
Test config/base_config.py
"""

from unittest import TestCase
from unittest.mock import MagicMock, patch

from templatron.config.base_config import BaseConfig


class TestBaseConfig(TestCase):
    """
    Test class for BaseConfig class
    """

    @classmethod
    def setUpClass(cls):
        cls.test_defaults = {"one": 1}
        BaseConfig.SAFE_DEFAULTS = cls.test_defaults

    def test_init_none_config_path(self):
        """
        Test BaseConfig.__init__() with config_path == None
        """

        result = BaseConfig(None)
        self.assertEqual(result.config, self.test_defaults)

    @patch("templatron.config.base_config.BaseConfig.load_config")
    def test_init_path_config_path(self, mock_load):
        """
        Test BaseConfig.__init__() with config_path set to a string
        """

        mock_load.return_value = {}
        result = BaseConfig("/path/to/config")
        self.assertEqual(result.config, self.test_defaults)
        mock_load.assert_called_with("/path/to/config")

    def test_get_valid(self):
        """
        Test BaseConfig.get(), which is a wrapper function
        """

        obj = BaseConfig(None)
        self.assertEqual(obj.get("one"), 1)

    def test_set_valid(self):
        """
        Test BaseConfig.set(), which is a wrapper function
        """

        obj = BaseConfig(None)
        obj.set("one", 2)
        self.assertEqual(obj.config["one"], 2)

    def test_log_config_logger_set(self):
        """
        Test BaseConfig.log_config when `self.logger` is set ahead of time.
        """

        obj = BaseConfig(None)
        obj.logger = MagicMock()
        obj.log_config()
        obj.logger.info.assert_called_with(f"with config:\n{self.test_defaults}")

    @staticmethod
    @patch("templatron.config.base_config.logging.getLogger")
    def test_log_config_logger_empty(mock_logging):
        """
        Test BaseConfig.log_config when `self.logger` is not set ahead of time.
        """

        obj = BaseConfig(None)
        obj.log_config()
        mock_logging.assert_called_with("BaseConfig")

    @patch("builtins.open", create=True)
    def test_load_config_empty_file(self, mock_open):
        """
        Test BaseConfig.load_config when config_path is an empty file
        """

        mock_open().__enter__().read.return_value = ""
        obj = BaseConfig(None)
        result = obj.load_config("fake_path")
        self.assertEqual(result, {})

    @patch("builtins.open", create=True)
    def test_load_config_with_hyphens(self, mock_open):
        """
        Test BaseConfig.load_config when config contains keys with hyphens
        """

        mock_open().__enter__().read.return_value = "first-key: 1"
        obj = BaseConfig(None)
        result = obj.load_config("fake_path")
        self.assertIn("first_key", result)

    @patch("builtins.open", create=True)
    def test_load_config_with_empty_vals(self, mock_open):
        """
        Test BaseConfig.load_config when config contains empty values
        """

        mock_open().__enter__().read.return_value = "empty: ''"
        obj = BaseConfig(None)
        result = obj.load_config("fake_path")
        self.assertEqual(type(result["empty"]), type(None))
        self.assertEqual(result["empty"], None)
