"""Tests for vmget colors module."""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from vmget.colors import (
    Colors,
    supports_color,
    success,
    error,
    warning,
    info,
    highlight,
    bold,
    dim,
    print_success,
    print_error,
    print_warning,
    print_info,
)


class TestSupportsColor:
    """Tests for supports_color function."""

    @patch.dict(os.environ, {"NO_COLOR": "1"})
    def test_no_color_env_disables_color(self):
        assert supports_color() is False

    @patch.dict(os.environ, {"FORCE_COLOR": "1"}, clear=False)
    @patch("sys.stdout")
    def test_force_color_env_enables_color(self, mock_stdout):
        mock_stdout.isatty.return_value = True
        # Remove NO_COLOR if set
        with patch.dict(os.environ, {"FORCE_COLOR": "1"}, clear=False):
            if "NO_COLOR" in os.environ:
                del os.environ["NO_COLOR"]
            assert supports_color() is True

    @patch("sys.stdout")
    def test_non_tty_disables_color(self, mock_stdout):
        mock_stdout.isatty.return_value = False
        assert supports_color() is False


class TestColors:
    """Tests for Colors class."""

    def test_colors_have_values(self):
        assert Colors.RED == "\033[31m"
        assert Colors.GREEN == "\033[32m"
        assert Colors.BLUE == "\033[34m"
        assert Colors.RESET == "\033[0m"

    def test_disable_and_enable(self):
        original = Colors._enabled
        Colors.disable()
        assert Colors._enabled is False
        Colors.enable()
        # Restore original state
        Colors._enabled = original


class TestColorFunctions:
    """Tests for color formatting functions."""

    def test_success_with_colors_disabled(self):
        Colors._enabled = False
        result = success("test")
        assert result == "test"
        Colors._enabled = True

    def test_error_with_colors_disabled(self):
        Colors._enabled = False
        result = error("test")
        assert result == "test"
        Colors._enabled = True

    def test_success_with_colors_enabled(self):
        Colors._enabled = True
        result = success("test")
        assert Colors.GREEN in result
        assert Colors.RESET in result

    def test_error_with_colors_enabled(self):
        Colors._enabled = True
        result = error("test")
        assert Colors.RED in result
        assert Colors.RESET in result

    def test_warning_with_colors_enabled(self):
        Colors._enabled = True
        result = warning("test")
        assert Colors.YELLOW in result

    def test_info_with_colors_enabled(self):
        Colors._enabled = True
        result = info("test")
        assert Colors.BLUE in result

    def test_highlight_with_colors_enabled(self):
        Colors._enabled = True
        result = highlight("test")
        assert Colors.CYAN in result

    def test_bold_with_colors_enabled(self):
        Colors._enabled = True
        result = bold("test")
        assert Colors.BOLD in result


class TestPrintFunctions:
    """Tests for print convenience functions."""

    def test_print_success(self, capsys):
        Colors._enabled = False
        print_success("Success message")
        captured = capsys.readouterr()
        assert "Success message" in captured.out

    def test_print_error_to_stderr(self, capsys):
        Colors._enabled = False
        print_error("Error message")
        captured = capsys.readouterr()
        assert "Error message" in captured.err

    def test_print_warning(self, capsys):
        Colors._enabled = False
        print_warning("Warning message")
        captured = capsys.readouterr()
        assert "Warning message" in captured.out

    def test_print_info(self, capsys):
        Colors._enabled = False
        print_info("Info message")
        captured = capsys.readouterr()
        assert "Info message" in captured.out
