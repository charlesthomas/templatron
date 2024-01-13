"""
Test functionality in log_or_print.py
"""

import io
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

from filesync.log_or_print import log_or_print


class TestLogOrPrint(TestCase):
    """
    Test log_or_print()
    """

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_log_or_print_big_effective_level(self, mock_stdout):
        """
        Test log_or_print when effective level > logging.{level}
        """

        mock_logger = MagicMock()
        mock_logger.getEffectiveLevel.return_value = logging.CRITICAL
        log_or_print(mock_logger, "Fake message", "info")
        self.assertEqual(mock_stdout.getvalue(), "Fake message\n")
        mock_logger.log.assert_not_called()

    @staticmethod
    def test_log_or_print_small_effective_level():
        """
        Test log_or_print when effective level > logging.{level}
        """

        mock_logger = MagicMock()
        mock_logger.getEffectiveLevel.return_value = logging.INFO
        log_or_print(mock_logger, "Fake message", "info")
        mock_logger.log.assert_called_with(logging.INFO, "Fake message")
